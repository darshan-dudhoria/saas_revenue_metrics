import pandas as pd

start_date = pd.to_datetime("01/01/2023")  # enter start date of the data
end_date = pd.to_datetime("12/31/2023")    # enter end date of the data

subscription_data = pd.read_csv(r'input_saas_revenue.csv')   # subscription data in CSV format

new_subscription_data = subscription_data.rename(columns={'Subscription Date': 'Date'})
new_subscription_data['Date'] = pd.to_datetime(new_subscription_data['Date'])

new_subscription_summary = pd.pivot_table(data=new_subscription_data,
                                          index=['Date', 'Plan', 'Payment cycle'],
                                          values='Amount',
                                          aggfunc='sum')

new_subscription_summary['Type of Transaction'] = "New"

churn_subscription_data1 = subscription_data.fillna(value={'Subscription End Date': "Ongoing"})
churn_subscription_data1 = churn_subscription_data1[churn_subscription_data1['Subscription End Date'] != "Ongoing"]
churn_subscription_data = churn_subscription_data1.copy(deep=True)

churn_subscription_data['Subscription End Date'] = pd.to_datetime(churn_subscription_data['Subscription End Date'])
churn_subscription_data = churn_subscription_data.rename(columns={'Subscription End Date': 'Date'})
churn_subscription_data['Amount'] = churn_subscription_data['Amount'].apply(lambda x: x*(-1))

churn_subscription_summary = pd.pivot_table(data=churn_subscription_data,
                                            index=['Date', 'Plan', 'Payment cycle'],
                                            values='Amount',
                                            aggfunc='sum')

churn_subscription_summary['Type of Transaction'] = "Churn"

new_churn_transactions = pd.concat([new_subscription_summary, churn_subscription_summary])


def equivalent_multiple(cycle):
    if cycle['Payment cycle'] == "Monthly":
        return 1
    elif cycle['Payment cycle'] == "Quarterly":
        return 1/3
    elif cycle['Payment cycle'] == "Annual":
        return 1/12
    else:
        return 1


new_churn_transactions.reset_index(inplace=True)

new_churn_transactions['Multiple'] = ''
new_churn_transactions['Multiple'] = new_churn_transactions.apply(equivalent_multiple, axis=1)

new_churn_transactions['Amount'] = new_churn_transactions['Amount'] * new_churn_transactions['Multiple']

new_churn_transactions_1 = pd.pivot_table(data=new_churn_transactions,
                                          index=['Plan', 'Date'],
                                          values='Amount',
                                          columns='Type of Transaction',
                                          aggfunc='sum')

new_churn_transactions_1.sort_index(axis=0, inplace=True)

list_of_dates = []

current_date = start_date

while current_date <= end_date:

    list_of_dates.append(current_date)
    current_date = current_date + pd.DateOffset(1)

date_list = pd.DataFrame(list_of_dates)
date_list.columns = ['Date']

list_of_plans = list(new_churn_transactions_1.index.unique('Plan'))

plans_list = pd.DataFrame(list_of_plans)
plans_list.columns = ['Plan']

plans_and_dates = plans_list.merge(date_list, how='cross')
plans_and_dates.set_index(['Plan', 'Date'], inplace=True)

summary_data = pd.merge(plans_and_dates, new_churn_transactions_1, left_index=True, right_index=True, how='outer')

summary_data = summary_data.fillna(value={'New': 0, 'Churn': 0})

summary_data['Opening MRR'] = ''
summary_data['Closing MRR'] = ''

new_subscription_location = summary_data.columns.get_loc('New')
churn_subscription_location = summary_data.columns.get_loc('Churn')
opening_mrr_location = summary_data.columns.get_loc('Opening MRR')
closing_mrr_location = summary_data.columns.get_loc('Closing MRR')


for plan in list_of_plans:

    opening_mrr = 0

    number_of_rows = summary_data.loc[plan].shape[0]
    a = summary_data.index.get_loc(plan)

    row_numbers = list(range(a.start, a.stop))

    for row_number in row_numbers:

        new_subscription = summary_data.iat[row_number, new_subscription_location]
        churn_subscription = summary_data.iat[row_number, churn_subscription_location]

        closing_mrr = opening_mrr + new_subscription + churn_subscription

        summary_data.iloc[row_number, opening_mrr_location] = opening_mrr
        summary_data.iloc[row_number, closing_mrr_location] = closing_mrr

        opening_mrr = closing_mrr

summary_data.to_csv('daily_planwise_mrr.csv')

daily_total_mrr = summary_data.reset_index()
daily_total_mrr = daily_total_mrr.drop(['Plan'], axis=1)
daily_total_mrr = daily_total_mrr.groupby(['Date']).sum()

daily_total_mrr.to_csv('daily_total_mrr.csv')


monthly_productwise_mrr = summary_data.reset_index()
monthly_productwise_mrr['Month and Year'] = monthly_productwise_mrr['Date'].dt.to_period('M')
monthly_productwise_mrr = monthly_productwise_mrr.drop(['Opening MRR', 'Closing MRR', 'Date'], axis=1)
monthly_productwise_mrr = monthly_productwise_mrr.groupby(['Plan', 'Month and Year']).sum()


monthly_productwise_mrr['Opening MRR'] = ''
monthly_productwise_mrr['Closing MRR'] = ''

monthly_new_subscription_location = monthly_productwise_mrr.columns.get_loc('New')
monthly_churn_subscription_location = monthly_productwise_mrr.columns.get_loc('Churn')
monthly_opening_mrr_location = monthly_productwise_mrr.columns.get_loc('Opening MRR')
monthly_closing_mrr_location = monthly_productwise_mrr.columns.get_loc('Closing MRR')

for plan in list_of_plans:

    monthly_opening_mrr = 0

    monthly_number_of_rows = monthly_productwise_mrr.loc[plan].shape[0]
    monthly_a = monthly_productwise_mrr.index.get_loc(plan)

    monthly_row_numbers = list(range(monthly_a.start, monthly_a.stop))

    for monthly_row_number in monthly_row_numbers:

        monthly_new_subscription = monthly_productwise_mrr.iat[monthly_row_number,
                                                               monthly_new_subscription_location]

        monthly_churn_subscription = monthly_productwise_mrr.iat[monthly_row_number,
                                                                 monthly_churn_subscription_location]

        monthly_closing_mrr = monthly_opening_mrr + monthly_new_subscription + monthly_churn_subscription

        monthly_productwise_mrr.iloc[monthly_row_number, monthly_opening_mrr_location] = monthly_opening_mrr
        monthly_productwise_mrr.iloc[monthly_row_number, monthly_closing_mrr_location] = monthly_closing_mrr

        monthly_opening_mrr = monthly_closing_mrr

monthly_productwise_mrr.to_csv('monthly_planwise_mrr.csv')


monthly_total_mrr = monthly_productwise_mrr.reset_index()
monthly_total_mrr = monthly_total_mrr.drop(['Plan'], axis=1)
monthly_total_mrr = monthly_total_mrr.groupby(['Month and Year']).sum()

monthly_total_mrr.to_csv('monthly_total_mrr.csv')
