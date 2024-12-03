# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 20:12:36 2024

@author: yehun_chang
"""

#%%
import pandas as pd
from scipy.stats import ttest_ind
#%%
data_excel = pd.ExcelFile('Users/yehun_chang/OneDrive/비디오/바탕 화면/대학원 공부 자료/24-2/텐서플로우 활용기초/숙제 실습/기말고사/AI 리뷰 요약 서비스 이용자 의도 파악(시트1순위형계산).xlsx')
data = data_excel.parse('설문지 응답 시트1')
#%%
male_ratings = data[data['1. 귀하의 성별은 무엇입니까?'] == '남자'][[
    '10. 만약 저희 AI 리뷰 요약 서비스를 웹으로 제공한다면 이 서비스를 이용하는 것이 쉬울 것이라고 생각하십니까?(용이성)',
    '11. 만약 저희 AI 리뷰 요약 서비스를 웹으로 제공한다면 유용할 것이라고 생각하십니까?(유용성)',
    '12. AI 리뷰 요약 서비스를 이용하는 것이 좋다고 생각하십니까? (태도)',
    '13. AI 리뷰요약 서비스가 상품 구매 시 귀하의 시간을 줄여준다면 리뷰 요약 서비스를 이용할 의도가 있습니까?'
]]

female_ratings = data[data['1. 귀하의 성별은 무엇입니까?'] == '여자'][[
    '10. 만약 저희 AI 리뷰 요약 서비스를 웹으로 제공한다면 이 서비스를 이용하는 것이 쉬울 것이라고 생각하십니까?(용이성)',
    '11. 만약 저희 AI 리뷰 요약 서비스를 웹으로 제공한다면 유용할 것이라고 생각하십니까?(유용성)',
    '12. AI 리뷰 요약 서비스를 이용하는 것이 좋다고 생각하십니까? (태도)',
    '13. AI 리뷰요약 서비스가 상품 구매 시 귀하의 시간을 줄여준다면 리뷰 요약 서비스를 이용할 의도가 있습니까?'
]]

t_test_results = {}
for column in male_ratings.columns:
    t_stat, p_value = ttest_ind(male_ratings[column], female_ratings[column], equal_var=False, nan_policy='omit')
    t_test_results[column] = {"t_statistic": t_stat, "p_value": p_value}

t_test_gender = pd.DataFrame(t_test_results).T
t_test_gender.index.name = '평가 항목'
t_test_gender.reset_index(inplace=True)
#%%
from scipy.stats import f_oneway

anova_results = []

research_list = [
    '10. 만약 저희 AI 리뷰 요약 서비스를 웹으로 제공한다면 이 서비스를 이용하는 것이 쉬울 것이라고 생각하십니까?(용이성)',
    '11. 만약 저희 AI 리뷰 요약 서비스를 웹으로 제공한다면 유용할 것이라고 생각하십니까?(유용성)',
    '12. AI 리뷰 요약 서비스를 이용하는 것이 좋다고 생각하십니까? (태도)',
    '13. AI 리뷰요약 서비스가 상품 구매 시 귀하의 시간을 줄여준다면 리뷰 요약 서비스를 이용할 의도가 있습니까?'
]

locations = data['3. 귀하의 거주지는 어디입니까?'].dropna().unique()

for question in research_list:
    anova_scores = [data.loc[data['3. 귀하의 거주지는 어디입니까?'] == location, question].dropna()
                    for location in locations]
    
    anova_result = f_oneway(*anova_scores)
    
    anova_results.append({
        '질문': question,
        'F-statistic': anova_result.statistic,
        'p-value': anova_result.pvalue
    })

anova_summary_location = pd.DataFrame(anova_results)
#%%
from statsmodels.stats.multicomp import pairwise_tukeyhsd

tukey_results = []

research_list_region = [
    '12. AI 리뷰 요약 서비스를 이용하는 것이 좋다고 생각하십니까? (태도)',
]

for question in research_list_region:
    tukey_data = data[['3. 귀하의 거주지는 어디입니까?', question]].dropna()

    tukey_result = pairwise_tukeyhsd(
        endog=tukey_data[question],
        groups=tukey_data['3. 귀하의 거주지는 어디입니까?'],
        alpha=0.05
    )
    
    tukey_df = pd.DataFrame(
        data=tukey_result._results_table.data[1:], 
        columns=tukey_result._results_table.data[0]
    )
    tukey_df['질문'] = question
    tukey_results.append(tukey_df)

all_tukey_region = pd.concat(tukey_results, ignore_index=True)
all_tukey_region
#%%
anova_results = []
age_groups = data['2. 귀하의 연령대는 무엇입니까?'].unique().tolist()

for question in research_list:
    anova_data = [data[data['2. 귀하의 연령대는 무엇입니까?'] == age_group][question].dropna()
                  for age_group in age_groups]
    
    f_stat, p_val = f_oneway(*anova_data)
    
    anova_results.append({
        '질문': question,
        'F-statistic': f_stat,
        'p-value': p_val
    })

anova_summary_age = pd.DataFrame(anova_results)
anova_summary_age
#%%
from statsmodels.stats.multicomp import pairwise_tukeyhsd

tukey_results = []

research_list_region = [
    '10. 만약 저희 AI 리뷰 요약 서비스를 웹으로 제공한다면 이 서비스를 이용하는 것이 쉬울 것이라고 생각하십니까?(용이성)',
    '11. 만약 저희 AI 리뷰 요약 서비스를 웹으로 제공한다면 유용할 것이라고 생각하십니까?(유용성)',
    '13. AI 리뷰요약 서비스가 상품 구매 시 귀하의 시간을 줄여준다면 리뷰 요약 서비스를 이용할 의도가 있습니까?'
]

for question in research_list_region:
    tukey_data = data[['2. 귀하의 연령대는 무엇입니까?', question]].dropna()

    tukey_result = pairwise_tukeyhsd(
        endog=tukey_data[question],
        groups=tukey_data['2. 귀하의 연령대는 무엇입니까?'],
        alpha=0.05
    )
    
    tukey_df = pd.DataFrame(
        data=tukey_result._results_table.data[1:], 
        columns=tukey_result._results_table.data[0]
    )
    tukey_df['질문'] = question
    tukey_results.append(tukey_df)

all_tukey_age = pd.concat(tukey_results, ignore_index=True)
all_tukey_age
#%%
anova_results = []
job_groups = data['4. 귀하의 직업은 무엇입니까?'].unique().tolist()

for question in research_list:
    anova_data = [data[data['4. 귀하의 직업은 무엇입니까?'] == job_group][question].dropna()
                  for job_group in job_groups]
    
    f_stat, p_val = f_oneway(*anova_data)
    
    anova_results.append({
        '질문': question,
        'F-statistic': f_stat,
        'p-value': p_val
    })

anova_summary_job = pd.DataFrame(anova_results)
anova_summary_job