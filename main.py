import tabula
import os

file = '/Users/jnofzige/workspace/personal/simple-pdf-table-parse-and-dedupe/pdf-source/MAGICTRAX_BY_SONG.pdf'

# read all pages of pdf into list of dataframe
#dataframes = tabula.read_pdf(file, pages='all',pandas_options={'header':None})

# read every row as if it were a row, no header
tabfile = tabula.read_pdf(file, pages=1, pandas_options={'header': None})

# tabfile is a list of tables found by tabula, we'll use the first to start
df = tabfile[0]

# based off of whether there is a NaN in what would have been the header, discard or keep

# shape[0] is number of rows in table
# shape[1] is number of columns in table
# iloc prints table based off row and column information - iloc[0:4, 0,6] would print rows 0-4 from columns 0-6
# this line removes the first row of a dataframe
df = df.iloc[1:df.shape[0], :]

# drop NaN columns if they have cells with NaN that cross a threshold
# https://stackoverflow.com/questions/31614804/how-to-delete-a-column-in-pandas-dataframe-based-on-a-condition
threshold_nan = 15

# removes rows with NaN count greater than threshold_nan
df = df.drop(df.columns[df.isnull().sum(axis=0) > threshold_nan], axis=1)

# you need to rename the rows to numbers again if you reshape these dataframes
# after removing a column, rename the columns
df.columns = range(df.shape[1])

# typically if a row has a bunch of NaN values and one actual value it's because the cell in the row above ran over one line
# using pad fill we can insert the values from the preceding line and use a dedupe method to locate adjacent cells with matching values
# not perfect but better than nothing you goofball
#df.fillna(method="pad", limit=1)

# another option is to id the rows with NaN values first
#df[df.isna().any(axis=1)]

# select a subset (slice) of NaN rows
# df[df.isna().any(axis=1)].loc[:9,:]

# get a list of that subset dataframes (nan only) indexes
# df[df.isna().any(axis=1)].index.values.tolist()

# create slices of the original dataframes with the preceding row for each nan row
# df[df.isna().any(axis=1)].index.values.tolist()

# keep the concatenated row by appending it to the clean dataframe
# drop the two nasty originals that you've now combined
for index in df[df.isna().any(axis=1)].index.values.tolist():
  # print NaN row and preceding row
  salmon = df.loc[index-1:index,:]
  # remove nan from nans - fill the nan with preceeding value
  salmon = salmon.fillna(method="pad", limit=1)
  # create new row by concatenating the two rows and grouping by any but the nonmatching
  # 0 is song title in test data
  # 1 is artist in test data
  # in this case, artist name ran over a line - we group by song title, and transform artist name, then reassign artist name
  salmon[1] = salmon.groupby([0])[1].transform(lambda x : ' '.join(x))
  new_row=salmon[1]
  # append BOTH new rows to parent df
  df = df.append(new_row, ignore_index=False)
  # drop BOTH originating rows from parent df
  # REMOVE all duplicates from parent df WITH KEEP feature enabled
  # Repeat for each key
  # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html
  print(df)


# turn NaN value to empty string with numpy
# or!!! df.fillna('', inplace=True)

# isolate the two lines which need to be merged
#for index in df2[df.isna().any(axis=1)].index.values.tolist():
#  df2.loc[index-1:index,:]

# concatenate the two lines to create one new row with values
salmon[1] = salmon.groupby([0])[1].transform(lambda x : ' '.join(x))

