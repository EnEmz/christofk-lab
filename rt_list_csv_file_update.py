import pandas as pd
from tkinter.filedialog import askopenfilename


newpath = askopenfilename()
new_df = pd.read_csv(newpath)


oldpath = askopenfilename()
old_df = pd.read_csv(oldpath)

for i in range(50):

    old_df['name'] = old_df['name'].map(lambda x: x.rstrip(f' M{i}'))

old_df = old_df.drop_duplicates(subset="name")
old_df = old_df.reset_index()
print(old_df)


for new_index, new_row in new_df.iterrows():
    for old_index, old_row in old_df.iterrows():

        fullstr = new_row["name"]
        substr = old_row["name"]

        if fullstr != None and substr in fullstr:
            new_df.at[new_index, "rt"] = old_row["rt"]
        

        else:
            pass


print(old_df)
print(new_df)

new_df.to_csv("updated_rt_list.csv", index = False)