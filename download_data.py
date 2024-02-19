import pandas as pd
import gdown

share_id="1oMXkfGv-FMPHFRCGF4VAPUK3vr6b97HoOW-RySnYenM" #id of gsheet
df=pd.read_csv(f"https://docs.google.com/spreadsheets/d/{share_id}/export?format=csv")

print(len(df.index))

for i in range(len(df.index)):
    file_url=df.iloc[i]['enter cv']
    output_path = f"applicant{i}.pdf"
    print(file_url)
    gdown.download(file_url, output_path, quiet=False, fuzzy=True) #download pdf


#print(df.iloc[0]['enter cv'])