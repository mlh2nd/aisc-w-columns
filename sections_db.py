import pandas as pd

def aisc_w_sections()->pd.DataFrame:
    filepath = "aisc_section_databases/aisc_w_db_us.csv"
    w_df = pd.read_csv(filepath).set_index("Section")
    return w_df


def sections_filter(df: pd.DataFrame, operator: str, **kwargs) -> pd.DataFrame:
    sub_df = df.copy()
    
    for parameter, value in kwargs.items():
        if operator == "ge":
            mask = sub_df[parameter] >= value
        elif operator == "le":
            mask = sub_df[parameter] <= value
        else:
            raise ValueError("Invalid comparison type")
        sub_df = sub_df.loc[mask]
    return sub_df


def sort_by_weight(df: pd.DataFrame, ascending: bool=True) -> pd.DataFrame:
    sub_df = df.copy()
    return sub_df.sort_values("W", ascending=ascending)
