import json
import re
import pandas as pd
from google.cloud import storage
from google.oauth2 import service_account
from user_definition import (bucket_name, file_name_prefixes,file_name_prefixes_static, project_id,
                            service_account_file_path)

#rate for the normalization of crime and outage rates
rate =1000
# population added by area name- fix misspelled names to match for join
nameFix = {"MONTCLAIRE": "MONTCLARE","WASHINGTON HEIGHT":"WASHINGTON HEIGHTS"}
#name the cols for join
incomeCols ={"Community Area Number": "community_area", "COMMUNITY AREA NAME": "community_name", "PER CAPITA INCOME ": "per_capita_income"}

# find the most recent dated file (prefix/YYYY-MM-DD.json) for a prefix in gcs
def latest_blob_name(bucket, prefix) -> str:
    pattern = re.compile(rf"^{prefix}/\d{{4}}-\d{{2}}-\d{{2}}\.json$")
    names = [blob.name for blob in bucket.list_blobs(prefix=f"{prefix}/")
             if pattern.match(blob.name)]
    if not names:
        raise FileNotFoundError(f"no dated files found under {prefix}/ in {bucket.name}")
    return max(names)


# get the data from gcs and reeady to prcess into data frame
def retrieve_data_from_gcs(service_account_key, project_id, 
                           bucket_name, file_name_prefixes,file_name_prefixes_static):
    credentials = service_account.Credentials.from_service_account_file(service_account_key)
    client = storage.Client(project=project_id,credentials=credentials)
    bucket = client.bucket(bucket_name)
    output= {}

    # scheduled data: newest file written by the scheduler for each prefix
    for prefix in file_name_prefixes:
        blob = bucket.blob(latest_blob_name(bucket, prefix))
        output[prefix] = json.loads(blob.download_as_bytes())

    for prefix in file_name_prefixes_static:
       blob = bucket.blob(f"{prefix}/{prefix}.json")
       output[prefix]=json.loads(blob.download_as_bytes())
    return output


def makeFrame(data: list, cols: dict = None) -> pd.DataFrame:
    df = pd.DataFrame(data)
    # if the columsn need to be renamed this function will be called with "cols" with correct col names
    if cols:
       df= df.rename(columns=cols)

     # 0 not an areacode for chicago, so assign as missing
    df["community_area"] =pd.to_numeric(df["community_area"], errors="coerce")
    df.loc[df["community_area"] == 0, "community_area"] = float("nan")
    df["community_area"]= df["community_area"].astype("Int64")
    return df


# do not need anymore for visualization since data does not need to be agg by month
#def aggMonthly(df: pd.DataFrame, date_col: str, name: str) -> pd.Series:
 #  df= df.assign(month=df[date_col].dt.to_period("M"))
  # df= df.groupby(["community_area", "month"]).size()
  # df=df.rename(name)
   #return df


# make uppercase, remove punctuation, spaces, adn include the misspelled fixes from population dataset
def alterName(name) -> str:
    text = str(name).upper()
    area = ""
    for char in text:
        if (char >= "A" and char <= "Z") or char == " ":
            area = area + char
    final = area.strip()

    if final in nameFix:
        return nameFix[final]
    
    return final


# assigns the population values to the correct community area code number
def makePopulation(data: list, income: pd.DataFrame) -> pd.DataFrame:
    population = pd.DataFrame(data)
    population = population.rename(columns={"Community Area": "area_name","Total Population": "population"})

    keysN =[]
    for name in population["area_name"]:
        keysN.append(alterName(name))
    population["key"] = keysN
    population["population"]= pd.to_numeric(population["population"])

    names = income[["community_area", "community_name"]].drop_duplicates().copy()
    keys = []
    for name in names["community_name"]:
        keys.append(alterName(name))
    names["key"] = keys

    population_data =population[["key", "population"]]
    output = names.merge(population_data,on="key",how="left")

    return output[["community_area", "population"]]


def get_data():
    data = retrieve_data_from_gcs(service_account_file_path, project_id, bucket_name, file_name_prefixes, file_name_prefixes_static)
    crime= makeFrame(data["crime"])
    light= makeFrame(data["light"])
    income= makeFrame(data["income"], incomeCols).dropna(subset=["community_area"])

    crime["date"] = pd.to_datetime(crime["date"], errors="coerce")
    light["created_date"] = pd.to_datetime(light["created_date"], errors="coerce")

    # remove rows with missing dates or community areas
    crime= crime.dropna(subset= ["date", "community_area"])
    light = light.dropna(subset= ["created_date", "community_area"])
   
    startDay = max(crime["date"].min(), light["created_date"].min()).normalize()
    end = min(crime["date"].max(), light["created_date"].max()).normalize()
    if startDay > end:
        raise ValueError("crime and outage date ranges do not overlap")
    endDay = end + pd.offsets.Day(1)

    # include crime and outage data for overlapping time range
    crime = crime[crime["date"].between(startDay, endDay, inclusive="left")]
    light = light[light["created_date"].between(startDay, endDay, inclusive="left")]

    #start with df with income
    df = income[["community_area", "community_name", "per_capita_income"]].drop_duplicates()
    
    # use qcut insteadof cut becasue it makes equal sized groups/ quantiles instead of using equal width ranges
    df["income_category"] = pd.qcut(df["per_capita_income"],q=3,labels=["Low", "Medium", "High"])

    # MERGES
    crime_counts = crime.groupby("community_area").size().rename("crime_count")
    df = df.merge(crime_counts, on="community_area", how="left")

    outage_counts = light.groupby("community_area").size().rename("outage_count")
    df = df.merge(outage_counts, on="community_area", how="left")

    population = makePopulation(data["population"], income)
    df = df.merge(population, on="community_area", how="left")

    # replace missing crime + outage counts w zero. convert counts to ints
    df[["crime_count", "outage_count"]] = (df[["crime_count", "outage_count"]].fillna(0).astype(int))

    # find rates for normalization, round 3 places
    df["crime_rate"]= (df["crime_count"] / df["population"] * rate).round(3)
    df["outage_rate"]= (df["outage_count"] / df["population"] * rate).round(3)

    #remove these cols simce visualizations do not need them in order to simplify
    df =df.drop(columns=["crime_count", "outage_count", "population"])

    return df.sort_values("community_area").reset_index(drop=True), data["geographic"], startDay.date(), end.date()



if __name__ == '__main__':
    df, geo, start_date, end_date = get_data()
    df.to_csv(f"df_{end_date}.csv", index=False)
    with open("geographic.geojson", "w") as f:
        json.dump(geo, f)

    print(df.head())
    print(f"overlapping date range: {start_date} to {end_date}")
