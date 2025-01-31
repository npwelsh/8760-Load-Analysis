C:\Users\Nolan Welsh\AppData\Local\Temp\ipykernel_7488\855086609.py:56: DeprecationWarning: DataFrameGroupBy.apply operated on the grouping columns. This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation. Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.
  outages_day = unmet_load_df.groupby(['month', 'day']).apply(count_consecutive_groups).reset_index()
  
  https://python-forum.io/thread-6792-post-33312.html#pid33312
  To make the complier better and leaner 