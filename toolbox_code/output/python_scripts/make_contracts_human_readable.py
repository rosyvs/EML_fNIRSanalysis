import pandas as pd

cond_map = {'aloc_sentences+bloc_words+cloc_jabsent+dloc_jabwords': "Localizer v. Not (Baseline)",
             'aloc_sentences-dloc_jabwords': "Federonko Contrast (Sent v. Wordlist)",
             'aloc_sentences-bloc_words+cloc_jabsent-dloc_jabwords': "Syntactic (Sentence v. Non Sentence)",
             'aloc_sentences+bloc_words-cloc_jabsent-dloc_jabwords': "Semantic (Words v. Non Words)"}

df = pd.read_csv("../loc_con_results.csv")
df["Contrast"] = df["cond"].map(cond_map)
df.to_csv("./loc_con_results_readable.csv", index=False)
