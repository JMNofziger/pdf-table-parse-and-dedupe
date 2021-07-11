import tabula, pandas, argparse
from os import walk

# show me all the rows when printing dataframes
pandas.set_option('display.max_rows', None)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, required=True)
    parser.add_argument('-t', '--type', choices=['d','directory','f','file'], type=str, default='f')
    return parser.parse_args()

def clean_table_dataframe(df):
    # Remove header row from table
    df = df.iloc[1:df.shape[0], :]

    # Drop null columns over threshold and reset table
    threshold_nan = 15
    df = df.drop(df.columns[df.isnull().sum(axis=0) > threshold_nan], axis=1)
    df.columns = range(df.shape[1])
    # ^ the table is now in order for cleaning up the NaN values
    return df

def concatenate_nan_artists(df):
  # loop through row indexes of any row with nan value in the song column (0) - this typically means artist runover
  for index in df[df[0].isna()].index.values.tolist():
    print('\n===========\n')
    # create two row sub_df from nan row index and preceding row index
    sub_df = df.loc[index-1:index,:]
    print(sub_df)
    # fill in any cell of the sub_df table with pad method
    sub_df = sub_df.fillna(method="pad", limit=1)
    # group subdf by title, concatenate artist cell values, assign to the sub_df artist column (1)
    sub_df[1] = sub_df.groupby([0])[1].transform(lambda x : ' '.join(x))
    print("#\n#\n", sub_df[:1])
    print('\n===========\n')
    # drop the row with nan value and the preceeding row from the dataframe
    df = df.drop(index=[index-1,index])
    # append a single merged values row from the subdf to the parent df
    df = df.append(sub_df[:1], ignore_index=False)
  return df

def concatenate_nan_titles(df):
  # loop through row indexes of any row with nan value in the artist column (1) - this typically means song title runover
  for index in df[df[1].isna()].index.values.tolist():
    print('\n===========\n')
    # create two row sub_df from nan row index and preceding row index
    sub_df = df.loc[index-1:index,:]
    print(sub_df)
    # fill in any cell of the sub_df table with pad method
    sub_df = sub_df.fillna(method="pad", limit=1)
    # group subdf by artist, concatenate song title cell values, assign to the sub_df song title column (0)
    sub_df[0] = sub_df.groupby([1]).transform(lambda x : ' '.join(x))
    print("#\n#\n", sub_df[:1])
    print('\n===========\n')
    # drop the row with nan value and the preceeding row from the dataframe
    df = df.drop(index=[index-1,index])
    # append a single merged values row from the subdf to the parent df
    df = df.append(sub_df[:1], ignore_index=False)
  return df

def main(args):
  if args.type == 'd' or args.type == 'directory':
      filenames = next(walk(args.path), (None, None, []))[2]
  else:
      filenames = [args.path]

  for filename in filenames:
    # Load table from file
    if args.type == 'd' or args.type == 'directory':
      filename = args.path+filename
    print(filename)
    tabfile = tabula.read_pdf(filename, pages='all', pandas_options={'header': None})
    daddy_df = pandas.DataFrame()
    for df in tabfile:
      df = clean_table_dataframe(df)
      precount = len(df.index)
      na_count = len(df[df.isna().any(axis=1)].index.values.tolist())

      # Diff the changes
      print('\n\nNOW ORGANIZING BY ARTIST\n\n')
      try:
          df = concatenate_nan_artists(df)
      except Exception:
          print(df)
      print('\n\nNOW ORGANIZING BY TITLE\n\n')
      try:
          df = concatenate_nan_titles(df)
      except Exception:
          print(df)

      # Reset row indexes and column lenght
      df = df.reset_index(drop=True)
      df.columns = range(df.shape[1])

      # Drop dupes and NaNs
      df = df.drop_duplicates(subset=None, keep='first', inplace=False)
      df = df.dropna()
      daddy_df = daddy_df.append(df)

      # Show me the dataframe
      print(df, f'\n\nStarted with {precount} row dataframe which had {na_count} NaN count and ended with {len(df.index)}')
    # Reset row indexes and column lenght
    daddy_df = daddy_df.reset_index(drop=True)
    daddy_df.columns = range(daddy_df.shape[1])
    print(daddy_df, f'\n\n daddy_df has {len(daddy_df)} rows')
    daddy_df.to_csv(filenames[0]+'.csv', quoting=1)

if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
