import pandas as pd

cond_map = {'aloc_sentences+bloc_words+cloc_jabsent+dloc_jabwords': "Localizer v. Baseline",
             'aloc_sentences-dloc_jabwords': "Federonko Contrast (Sentences v. Non-words)",
             'aloc_sentences-bloc_words+cloc_jabsent-dloc_jabwords': "Syntactic",
             'aloc_sentences+bloc_words-cloc_jabsent-dloc_jabwords': "Semantic",
             'aloc_sentences-bloc_words-cloc_jabsent+dloc_jabwords': "Sem*Syn Interaction"
             }

df = pd.read_csv("../loc_con_results.csv")
df["Contrast"] = df["cond"].map(cond_map)
df.to_csv("./loc_con_results_readable.csv", index=False)
