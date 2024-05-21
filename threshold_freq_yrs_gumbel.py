import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson, chisquare, chi2_contingency, chi2
from scipy.optimize import minimize
from scipy.stats import gumbel_r

# Define the likelihood function for a Gumbel distribution
def gumbel_likelihood(params, data):
    loc = params[0]
    scale = params[1]
    log_likelihood = np.sum(np.log(gumbel_r.pdf(data, loc=loc, scale=scale)))
    return -log_likelihood






data=pd.read_excel(io='eqList2024_04_28.xlsx' , sheet_name="Sheet1", dtype={'Year':int,'Magnitude':float})

start = 3
end = 6.0
interval = 0.2

M_threshold_list = []
current = start

while current < end:
    M_threshold_list.append(current)
    current += interval
print(M_threshold_list)

data["Time"] = data['Time'].str[:7]
data[['Year', 'Month']] = data['Time'].str.split('-', expand=True)[[0,1]]
data['Month'] = data['Month'].astype(int)

# Determine half of the year based on the month
data['HalfYear'] = data['Month'].apply(lambda x: 'First Half' if x <= 6 else 'Second Half')

dataframes = []
fig, axes = plt.subplots(nrows=3, ncols=len(M_threshold_list)//3)

for thr in M_threshold_list:
    temp_data = data.loc[(data['Magnitude'] >= thr)]
    M_temp_result = temp_data.groupby(['Year', "HalfYear"]).size().reset_index(name='counts')
    dataframes.append(M_temp_result)
    
result = {
    'Magnitude_Threshold': [],
    'loc^': [],
    'scale^': [], 
    'Chi2_value': [],
    'Critical_value':[],
    'Accepted/Rejected':[]
    }

result_df = pd.DataFrame(result)

print("dataframes", dataframes)

for i, df in enumerate(dataframes):
    # print(df)
    ax = axes.flatten()[i]
    x = np.arange(0, max(df['counts'])+1 )  # Define the range of x values

    # Estimate the parameters using maximum likelihood estimation
    initial_guess = [0, 1]  # Initial guess for the parameters (loc, scale)
    result = minimize(gumbel_likelihood, initial_guess, args=(np.array(df['counts'].tolist()),), method='Nelder-Mead')
    estimated_loc, estimated_scale = result.x

    gumbel_dist = gumbel_r.pdf(x, loc=estimated_loc, scale=estimated_scale)* len(df['counts'])  # Calculate the Poisson probability mass function
    # gumbel_dist *= sum(df['counts'])/sum(gumbel_dist)
    gumbel_dist += 0.01
    #########################  Chi-Square Test Part
    observed_freq, _ = np.histogram(df['counts'], bins=np.arange(0, max(df['counts'])+1 ))
    observed_freq = observed_freq+0.01
    chi2_value = 0
    for o in range(len(observed_freq)):
        if observed_freq[o]>=1:
            diff = observed_freq[o]-gumbel_dist[o]
            chi2_value += (diff**2)/gumbel_dist[o]
    # print("chi2_value")
    degrees_of_freedom = len(np.unique(df['counts']))-1
    critical_value = chi2.ppf(1 - 0.05, degrees_of_freedom)
    #########################
    df['counts'].plot(kind='hist', bins=100,ax=ax, edgecolor='black', alpha=0.5,  label='Histogram')
    ax.plot(x, gumbel_dist, '.-', label='Poisson Distribution')
    ax.set_xlabel(f'# of EQ with M>{round(M_threshold_list[i],1)}')
    ax.set_ylabel('#(0.5yr)')
    ax.grid(True)

    ##########Appending Data to a dataframe  Magnitude of exceedance Annual rate Total difference Critical value Model accepted/rejected
    if (chi2_value > critical_value):
        acc_or_rej = "Rejected"
    else:
        acc_or_rej = "Accepted"
    # Create a new row
    new_row = pd.Series([M_threshold_list[i], estimated_loc,estimated_scale, chi2_value, critical_value, acc_or_rej], index=result_df.columns)
    # Append the new row
    result_df = result_df.append(new_row, ignore_index=True)
    ##########

print(result_df)
# Adjust spacing between subplots
plt.tight_layout()
# Show the plot
plt.show()