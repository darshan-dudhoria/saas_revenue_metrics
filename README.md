# SaaS Revenue Metrics (MRR)
This is a python script to calculate Monthly Recurring Revenue (MRR), which is among the most important revenue metrics for a SaaS business.

The MRR metric, being a non-GAAP metric, is not easily ascertainable from the accounting and financial records of the business.

This script helps in calculation of MRR on a day-wise and monthly basis.

## Features
Supports calculation for multiple types of customer subscription plans. It will give output on plan-wise and overall basis.

Supports calculation for customers paying on monthly, quarterly and annual basis. The script will automatically normalize those into monthly amounts for purposes of MRR.

## Input Format
The subscription register input should be in CSV format.

Columns: Subscription Date | Customer ID | Plan | Payment cycle | Amount | Subscription End Date

Subscription Date and End Date should be in dd mmmm yyyy format.

Payment cycle should be “Monthly”, “Quarterly” or “Annual”.

The input file should contain list of all customer subscriptions.

## Output
Output will be in the form of four CSV files.

1st file: Daily plan-wise new MRR, churn MRR and closing MRR.

2nd file: Daily total new MRR, churn MRR and closing MRR.

3rd file: Monthly plan-wise new MRR, churn MRR and closing MRR.

4nd file: Monthly total new MRR, churn MRR and closing MRR.

## Note

Though we have taken adequate care to create this script, however there may have been errors or omissions. The author is not responsible for such errors. This script is provided as-is with no warranties. 

This script will be suited for specific situations only and there might be various business situations which the script does not support at present.

Please consult professionals before taking any decisions.

For any feedback, please contact on hi@darshandudhoria.com

