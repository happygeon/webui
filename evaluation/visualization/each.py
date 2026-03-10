import json
import pandas as pd
import matplotlib.pyplot as plt

# Load the analyzed_queries.json file
with open("./analyzed_queries.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# 1. Application Category (industry_domain) summary
app_counts = df['industry_domain'].value_counts()
app_summary = pd.Series({
    'total_entries': len(df),
    'unique_categories': app_counts.shape[0],
    'mean_freq': app_counts.mean(),
    'max_freq': app_counts.max(),
    'min_freq': app_counts.min()
}, name='application_category')

# 2. Page Type summary
page_counts = df['page_type'].value_counts()
page_summary = pd.Series({
    'total_entries': len(df),
    'unique_page_types': page_counts.shape[0],
    'mean_freq': page_counts.mean(),
    'max_freq': page_counts.max(),
    'min_freq': page_counts.min()
}, name='page_type')

# 3. Widget summary (explode widgets list)
df_widgets = df.explode('widgets')
widget_counts = df_widgets['widgets'].value_counts()
widget_summary = pd.Series({
    'total_occurrences': len(df_widgets),
    'unique_widgets': widget_counts.shape[0],
    'mean_freq': widget_counts.mean(),
    'max_freq': widget_counts.max(),
    'min_freq': widget_counts.min()
}, name='widget')

# Combine summaries into one DataFrame
summary_df = pd.DataFrame([app_summary, page_summary, widget_summary])
import ace_tools as tools;
tools.display_dataframe_to_user(name="Summary Statistics for Categories", dataframe=summary_df)

# Plotting Top N for each
# 1. Top 10 Application Categories
plt.figure()
app_counts.head(10).plot(kind='bar')
plt.title('Application Categories by Frequency')
plt.xlabel('Application Category')
plt.ylabel('Frequency')
plt.tight_layout()

# 2. Top 10 Page Types
plt.figure()
page_counts.head(10).plot(kind='bar')
plt.title('Page Types by Frequency')
plt.xlabel('Page Type')
plt.ylabel('Frequency')
plt.tight_layout()

# 3. Top 15 Widgets
plt.figure()
widget_counts.head(15).plot(kind='bar')
plt.title('Widgets by Occurrence')
plt.xlabel('Widget')
plt.ylabel('Occurrences')
plt.tight_layout()

plt.show()
