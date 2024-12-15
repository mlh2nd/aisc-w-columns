import pandas as pd
import sections_db as sd

test_df = pd.DataFrame({"A":[3, 6, 9, 12],
                       "B":[4, 8, 12, 16],
                       "C":[5, 10, 15, 20],
                       "D":[6, 12, 18, 24]})


def test_sections_filter():
    B_le_10 = sd.sections_filter(test_df, "le", B=10)
    le_answer = pd.DataFrame({  "A":[3, 6],
                                "B":[4, 8],
                                "C":[5, 10],
                                "D":[6, 12]})
    
    C_ge_13 = sd.sections_filter(test_df, "ge", C=13).reset_index(drop=True)
    ge_answer = pd.DataFrame({  "A":[9, 12],
                                "B":[12, 16],
                                "C":[15, 20],
                                "D":[18, 24]})
    
    assert B_le_10.equals(le_answer)
    assert C_ge_13.equals(ge_answer)