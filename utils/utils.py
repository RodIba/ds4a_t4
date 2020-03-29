def plugins_options(dt:'pd.DataFrame', col1:str, col2:str):

    # Dropwdown options for col1
    f_1 = list(dt[col1].unique())
    f_1 = [x for x in f_1 if x]
    opt_1 = [{'label' : i, 'value' : i} for i in f_1]

    # Dropdown options for col2 
    f_2 = list(dt.columns[3:])
    opt_2 = [{'label' : i, 'value' : i} for i in f_2]

    # Time Slider options 
    dates = list(dt[col2].astype(str).unique())
    dates = [x for x in dates if x]

    return opt_1, opt_2, dates  
