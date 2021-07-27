# -*- coding: utf-8 -*-
"""DB2018L_ECommerceDataExploration_2021.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1prmH0-1RsJgmmXKjVaC15KTNDPfgHsaF

# CS145: Project 3 | E-commerce Dataset with Biq Query

## Collaborators:
Please list the names and SUNet IDs of your collaborators below:
* Arslan Ali, 2018-CE-236
* Muhammad Bilal, 2018-CE-247

**Setting Up BigQuery and Dependencies**
"""

# Run this cell to authenticate yourself to BigQuery
from google.colab import auth
auth.authenticate_user()
project_id = "db-prj-ml"

# Initialize BiqQuery client
from google.cloud import bigquery
client = bigquery.Client(project=project_id)

# Commented out IPython magic to ensure Python compatibility.
# Add imports for any visualization libraries you may need
import matplotlib.pyplot as plt

# %matplotlib inline

"""## Project Overview

1- Description:
The data analyst team at your Company exported the Google Analytics logs for an ecommerce website into BigQuery and created a new table of all the raw ecommerce visitor session data for me to explore. Using this data, I’ll try to answer a few questions.

Question1: Out of the total visitors who visited our website, what % made a purchase?

Question2: How many visitors bought on subsequent visits to the website?

Question3: What are some of the reasons a typical ecommerce customer will browse but not buy until a later visit?

Question4: Create a Machine Learning model in BigQuery to predict whether or not a new user is likely to purchase in the future. Identifying these high-value users can help the marketing team target them with special promotions and ad campaigns to ensure a conversion while they comparison shop between visits to your ecommerce site.

## Analysis of Dataset

---

*TODO: Analysis of your dataset*



----

## Data Exploration

---

*TODO: Exploring your questions, with appropriate visualizations*

---

##Question 1
"""

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# WITH visitors AS(
# SELECT
# COUNT(DISTINCT fullVisitorId) AS total_visitors
# FROM `data-to-insights.ecommerce.web_analytics`
# ),
# 
# purchasers AS(
# SELECT
# COUNT(DISTINCT fullVisitorId) AS total_purchasers
# FROM `data-to-insights.ecommerce.web_analytics`
# WHERE totals.transactions IS NOT NULL
# )
# 
# SELECT
#   total_visitors,
#   total_purchasers,
#   total_purchasers / total_visitors AS conversion_rate
# FROM visitors, purchasers

"""##Question 2"""

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# SELECT
#   p.v2ProductName,
#   p.v2ProductCategory,
#   SUM(p.productQuantity) AS units_sold,
#   ROUND(SUM(p.localProductRevenue/1000000),2) AS revenue
# FROM `data-to-insights.ecommerce.web_analytics`,
# UNNEST(hits) AS h,
# UNNEST(h.product) AS p
# GROUP BY 1, 2
# ORDER BY revenue DESC
# LIMIT 5;

"""##Q3:

### visitors who bought on a return visit could have bought on first.
"""

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# WITH all_visitor_stats AS (
# SELECT
#   fullvisitorid, # 741,721 unique visitors
#   IF(COUNTIF(totals.transactions > 0 AND totals.newVisits IS NULL) > 0, 1, 0) AS will_buy_on_return_visit
#   FROM `data-to-insights.ecommerce.web_analytics`
#   GROUP BY fullvisitorid
# )
# 
# SELECT
#   COUNT(DISTINCT fullvisitorid) AS total_visitors,
#   will_buy_on_return_visit
# FROM all_visitor_stats
# GROUP BY will_buy_on_return_visit

"""Analyzing the results, we can see that (11873 / 741721) = 1.6% of total visitors will return and purchase from the website. This includes the subset of visitors who bought on their very first session and then came back and bought again."""

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# 
# select
#   COUNT(DISTINCT fullVisitorId) AS unique_visitors,
#   channelGrouping
# FROM `data-to-insights.ecommerce.all_sessions`
# GROUP BY channelGrouping
# ORDER BY channelGrouping DESC;

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# 
# SELECT
#   (v2ProductName) AS ProductName
# FROM `data-to-insights.ecommerce.all_sessions`
# GROUP BY ProductName
# ORDER BY ProductName

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# 
# SELECT
#   COUNT(*) AS product_views,
#   (v2ProductName) AS ProductName
# FROM `data-to-insights.ecommerce.all_sessions`
# WHERE type = 'PAGE'
# GROUP BY v2ProductName
# ORDER BY product_views DESC
# LIMIT 5;

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# 
# WITH unique_product_views_by_person AS (
# -- find each unique product viewed by each visitor
# SELECT
#  fullVisitorId,
#  (v2ProductName) AS ProductName
# FROM `data-to-insights.ecommerce.all_sessions`
# WHERE type = 'PAGE'
# GROUP BY fullVisitorId, v2ProductName )
# 
# 
# -- aggregate the top viewed products and sort them
# SELECT
#   COUNT(*) AS unique_view_count,
#   ProductName
# FROM unique_product_views_by_person
# GROUP BY ProductName
# ORDER BY unique_view_count DESC
# LIMIT 5

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# 
# SELECT
#   COUNT(*) AS product_views,
#   COUNT(productQuantity) AS orders,
#   SUM(productQuantity) AS quantity_product_ordered,
#   v2ProductName
# FROM `data-to-insights.ecommerce.all_sessions`
# WHERE type = 'PAGE'
# GROUP BY v2ProductName
# ORDER BY product_views DESC
# LIMIT 5;

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# 
# SELECT
#   COUNT(*) AS product_views,
#   COUNT(productQuantity) AS orders,
#   SUM(productQuantity) AS quantity_product_ordered,
#   SUM(productQuantity) / COUNT(productQuantity) AS avg_per_order,
#   (v2ProductName) AS ProductName
# FROM `data-to-insights.ecommerce.all_sessions`
# WHERE type = 'PAGE'
# GROUP BY v2ProductName
# ORDER BY product_views DESC
# LIMIT 5;

"""## Data Prediction

**Selecting features**

1- Select features and create training dataset.

we have decided to test whether these two fields are good inputs for my classification model:

totals.bounces (whether the visitor left the website immediately)

totals.timeOnSite (how long the visitor was on our website)
"""

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# SELECT
#   * EXCEPT(fullVisitorId)
# FROM
# 
#   # features
#   (SELECT
#     fullVisitorId,
#     IFNULL(totals.bounces, 0) AS bounces,
#     IFNULL(totals.timeOnSite, 0) AS time_on_site
#   FROM
#     `data-to-insights.ecommerce.web_analytics`
#   WHERE
#     totals.newVisits = 1)
#   JOIN
#   (SELECT
#     fullvisitorid,
#     IF(COUNTIF(totals.transactions > 0 AND totals.newVisits IS NULL) > 0, 1, 0) AS will_buy_on_return_visit
#   FROM
#       `data-to-insights.ecommerce.web_analytics`
#   GROUP BY fullvisitorid)
#   USING (fullVisitorId)
# ORDER BY time_on_site DESC
# LIMIT 10;

"""Question: Which fields are the input features and the label?

Answer: The inputs are bounces and time_on_site. The label is will_buy_on_return_visit.

Question: Which two fields are known after a visitor’s first session?

Answer: bounces and time_on_site are known after a visitor’s first session.

**creating dataset**

**Creating Model:**
"""

# Commented out IPython magic to ensure Python compatibility.
# #Select features and create your training dataset
# %%bigquery --project $project_id
# SELECT
#   * EXCEPT(fullVisitorId)
# FROM
# 
#   # features
#   (SELECT
#     fullVisitorId,
#     IFNULL(totals.bounces, 0) AS bounces,
#     IFNULL(totals.timeOnSite, 0) AS time_on_site
#   FROM
#     `data-to-insights.ecommerce.web_analytics`
#   WHERE
#     totals.newVisits = 1)
#   JOIN
#   (SELECT
#     fullvisitorid,
#     IF(COUNTIF(totals.transactions > 0 AND totals.newVisits IS NULL) > 0, 1, 0) AS will_buy_on_return_visit
#   FROM
#       `data-to-insights.ecommerce.web_analytics`
#   GROUP BY fullvisitorid)
#   USING (fullVisitorId)
# ORDER BY time_on_site DESC
# LIMIT 10;

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# 
# CREATE OR REPLACE MODEL `bqml_ecomm.model`
# OPTIONS
# (
# model_type='logistic_reg',
# labels = ['will_buy_on_return_visit']
# )
# AS
# 
# #standardSQL
# SELECT
#   * EXCEPT(fullVisitorId)
# FROM
# 
#   # features
#   (SELECT
#     fullVisitorId,
#     IFNULL(totals.bounces, 0) AS bounces,
#     IFNULL(totals.timeOnSite, 0) AS time_on_site
#   FROM
#     `data-to-insights.ecommerce.web_analytics`
#   WHERE
#     totals.newVisits = 1
#     AND date BETWEEN '20160801' AND '20170430') # train on first 9 months
#   JOIN
#   (SELECT
#     fullvisitorid,
#     IF(COUNTIF(totals.transactions > 0 AND totals.newVisits IS NULL) > 0, 1, 0) AS will_buy_on_return_visit
#   FROM
#       `data-to-insights.ecommerce.web_analytics`
#   GROUP BY fullvisitorid)
#   USING (fullVisitorId)
# ;
#

"""**Evaluating:**"""

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# 
# SELECT
#   roc_auc,
#   CASE
#     WHEN roc_auc > .9 THEN 'good'
#     WHEN roc_auc > .8 THEN 'fair'
#     WHEN roc_auc > .7 THEN 'not great'
#   ELSE 'poor' END AS model_quality
# FROM
#   ML.EVALUATE(MODEL `bqml_ecomm.model`,  (
# 
# SELECT
#   * EXCEPT(fullVisitorId)
# FROM
# 
#   # features
#   (SELECT
#     fullVisitorId,
#     IFNULL(totals.bounces, 0) AS bounces,
#     IFNULL(totals.timeOnSite, 0) AS time_on_site
#   FROM
#     `data-to-insights.ecommerce.web_analytics`
#   WHERE
#     totals.newVisits = 1
#     AND date BETWEEN '20170430' and '20170630') # train on first 9 months
#   JOIN
#   (SELECT
#     fullvisitorid,
#     IF(COUNTIF(totals.transactions > 0 AND totals.newVisits IS NULL) > 0, 1, 0) AS will_buy_on_return_visit
#   FROM
#       `data-to-insights.ecommerce.web_analytics`
#   GROUP BY fullvisitorid)
#   USING (fullVisitorId);)
# 
# )
# )
# 
# 
# 
#

"""**Recreating model after adding more features:**"""

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# 
# CREATE OR REPLACE MODEL `bqml_ecomm.model`
# OPTIONS
#   (model_type='logistic_reg', labels = ['will_buy_on_return_visit']) AS
# 
# WITH all_visitor_stats AS (
# SELECT
#   fullvisitorid,
#   IF(COUNTIF(totals.transactions > 0 AND totals.newVisits IS NULL) > 0, 1, 0) AS will_buy_on_return_visit
#   FROM `data-to-insights.ecommerce.web_analytics`
#   GROUP BY fullvisitorid
# )
# 
# # add in new features
# SELECT * EXCEPT(unique_session_id) FROM (
# 
#   SELECT
#       CONCAT(fullvisitorid, CAST(visitId AS STRING)) AS unique_session_id,
# 
#       # labels
#       will_buy_on_return_visit,
# 
#       MAX(CAST(h.eCommerceAction.action_type AS INT64)) AS latest_ecommerce_progress,
# 
#       # behavior on the site
#       IFNULL(totals.bounces, 0) AS bounces,
#       IFNULL(totals.timeOnSite, 0) AS time_on_site,
#       totals.pageviews,
# 
#       # where the visitor came from
#       trafficSource.source,
#       trafficSource.medium,
#       channelGrouping,
# 
#       # mobile or desktop
#       device.deviceCategory,
# 
#       # geographic
#       IFNULL(geoNetwork.country, "") AS country
# 
#   FROM `data-to-insights.ecommerce.web_analytics`,
#      UNNEST(hits) AS h
# 
#     JOIN all_visitor_stats USING(fullvisitorid)
# 
#   WHERE 1=1
#     # only predict for new visits
#     AND totals.newVisits = 1
#     AND date BETWEEN '20160801' AND '20170430' # train 9 months
# 
#   GROUP BY
#   unique_session_id,
#   will_buy_on_return_visit,
#   bounces,
#   time_on_site,
#   totals.pageviews,
#   trafficSource.source,
#   trafficSource.medium,
#   channelGrouping,
#   device.deviceCategory,
#   country
# );
#

"""**Evaluating:**"""

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# 
# SELECT
#   roc_auc,
#   CASE
#     WHEN roc_auc > .9 THEN 'good'
#     WHEN roc_auc > .8 THEN 'fair'
#     WHEN roc_auc > .7 THEN 'not great'
#   ELSE 'poor' END AS model_quality
# FROM
#   ML.EVALUATE(MODEL `bqml_ecomm.model`,  (
# 
# WITH all_visitor_stats AS (
# SELECT
#   fullvisitorid,
#   IF(COUNTIF(totals.transactions > 0 AND totals.newVisits IS NULL) > 0, 1, 0) AS will_buy_on_return_visit
#   FROM `data-to-insights.ecommerce.web_analytics`
#   GROUP BY fullvisitorid
# )
# 
# # add in new features
# SELECT * EXCEPT(unique_session_id) FROM (
# 
#   SELECT
#       CONCAT(fullvisitorid, CAST(visitId AS STRING)) AS unique_session_id,
# 
#       # labels
#       will_buy_on_return_visit,
# 
#       MAX(CAST(h.eCommerceAction.action_type AS INT64)) AS latest_ecommerce_progress,
# 
#       # behavior on the site
#       IFNULL(totals.bounces, 0) AS bounces,
#       IFNULL(totals.timeOnSite, 0) AS time_on_site,
#       totals.pageviews,
# 
#       # where the visitor came from
#       trafficSource.source,
#       trafficSource.medium,
#       channelGrouping,
# 
#       # mobile or desktop
#       device.deviceCategory,
# 
#       # geographic
#       IFNULL(geoNetwork.country, "") AS country
# 
#   FROM `data-to-insights.ecommerce.web_analytics`,
#      UNNEST(hits) AS h
# 
#     JOIN all_visitor_stats USING(fullvisitorid)
# 
#   WHERE 1=1
#     # only predict for new visits
#     AND totals.newVisits = 1
#     AND date BETWEEN '20170501' AND '20170630' # eval 2 months
# 
#   GROUP BY
#   unique_session_id,
#   will_buy_on_return_visit,
#   bounces,
#   time_on_site,
#   totals.pageviews,
#   trafficSource.source,
#   trafficSource.medium,
#   channelGrouping,
#   device.deviceCategory,
#   country
# )
# ));
#

"""**Prediction:**"""

# Commented out IPython magic to ensure Python compatibility.
# %%bigquery --project $project_id
# 
# SELECT
# *
# FROM
#   ml.PREDICT(MODEL `bqml_ecomm.model`,
#    (
# 
# WITH all_visitor_stats AS (
# SELECT
#   fullvisitorid,
#   IF(COUNTIF(totals.transactions > 0 AND totals.newVisits IS NULL) > 0, 1, 0) AS will_buy_on_return_visit
#   FROM `data-to-insights.ecommerce.web_analytics`
#   GROUP BY fullvisitorid
# )
# 
#   SELECT
#       CONCAT(fullvisitorid, '-',CAST(visitId AS STRING)) AS unique_session_id,
# 
#       # labels
#       will_buy_on_return_visit,
# 
#       MAX(CAST(h.eCommerceAction.action_type AS INT64)) AS latest_ecommerce_progress,
# 
#       # behavior on the site
#       IFNULL(totals.bounces, 0) AS bounces,
#       IFNULL(totals.timeOnSite, 0) AS time_on_site,
#       totals.pageviews,
# 
#       # where the visitor came from
#       trafficSource.source,
#       trafficSource.medium,
#       channelGrouping,
# 
#       # mobile or desktop
#       device.deviceCategory,
# 
#       # geographic
#       IFNULL(geoNetwork.country, "") AS country
# 
#   FROM `data-to-insights.ecommerce.web_analytics`,
#      UNNEST(hits) AS h
# 
#     JOIN all_visitor_stats USING(fullvisitorid)
# 
#   WHERE
#     # only predict for new visits
#     totals.newVisits = 1
#     AND date BETWEEN '20170701' AND '20170801' # test 1 month
# 
#   GROUP BY
#   unique_session_id,
#   will_buy_on_return_visit,
#   bounces,
#   time_on_site,
#   totals.pageviews,
#   trafficSource.source,
#   trafficSource.medium,
#   channelGrouping,
#   device.deviceCategory,
#   country
# )
# 
# )
# 
# ORDER BY
#   predicted_will_buy_on_return_visit DESC;
#

"""## Conclusion

---

*TODO:
 Final conclusions based on the rest of your project*
Of the top 6% of first-time visitors (sorted in decreasing order of predicted

probability), more than 6% make a purchase in a later visit.

These users represent nearly 50% of all first-time visitors who make a purchase

in a later visit.

Overall, only 0.7% of first-time visitors make a purchase in a later visit.

Targeting the top 6% of first-time increases marketing ROI by 9x vs targeting 

them all!
---
"""

