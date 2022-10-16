
import pandas as pd
import glob
import tqdm

def clean_df(df: pd.DataFrame):
	output_df = []
	for _, row in df.iterrows():
		if str(row["Close"]) != "nan":
			output_df.append(row)
	output_df = pd.DataFrame(output_df)
	return output_df


if __name__ == "__main__":
	files = glob.glob("Commodity/*.csv")

	for csv_file in tqdm.tqdm(files):
		loaded_df = pd.read_csv(csv_file)
		sanitized_df = clean_df(loaded_df)
		output_filename = csv_file.replace(".csv", "_sanitized.csv")
		sanitized_df.to_csv(output_filename)



