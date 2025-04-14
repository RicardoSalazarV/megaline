# ## Inicialización

# Para realizar un oportuno análisis de los datos proporcionados, primero deberemos identificar los "errores" que estén en cada uno de los dataframes. Necesitaremos convertir todo dato que sea materia prima para futuros cálculos en el tipo "int" y las fechas a "datetime". Esto permitirá el flujo de trabajo en las futuras líneas que requieran cálculos matemáticos o agrupaciones.
# 
# Para lograr, en la parte final de este proyecto, analizar estadísticamente la información, deberemos entender los resultados de nuestro primer análisis. A través de recursos gráficos como histogramas, gráficas y gráficas de caja, podremos diseñar un experimento que nos permita justificar la hipótesis que seleccionemos.



import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math as mt 
from math import factorial
import seaborn as sns
from scipy import stats


# ## Cargar datos



calls= pd.read_csv("/datasets/megaline_calls.csv") 
internet= pd.read_csv("/datasets/megaline_internet.csv")
messages=pd.read_csv("/datasets/megaline_messages.csv") 
plans=pd.read_csv("/datasets/megaline_plans.csv") 
users=pd.read_csv("/datasets/megaline_users.csv")


# ## Preparar los datos

# ## Tarifas
print(plans.head().info())
print(plans.head())


# Para este primer vistazo parece que no requerimos algun ajuste

# ## Corregir datos

# ## Enriquecer los datos

print(users.info())

print(users.head())

# Basados en el diccionario de datos "churn_date" hace refencia a la fecha en que se dejo el servicio, podemos sustituir el valor "NaN" por "0" para futuros calculos 

# ### Corregir los datos

users["churn_date"]=users["churn_date"].fillna(0)
print(users.info())


# ### Enriquecer los datos

# ## Llamadas
print(calls.info())
print(calls.head())


# Basados en la primera observacion podemos necesitar los datos relacionados a fechas en formato "datetime", esto nos permitira su uso con los metodos correspondientes mas adelante 

# ### Corregir los datos

calls["call_date"] = pd.to_datetime(calls["call_date"], format="%Y-%m-%d")
print(calls.info())


# ### Enriquecer los datos

calls["call_date"] = pd.to_datetime(calls["call_date"])
calls["month"] = calls["call_date"].dt.to_period("M")


# ## Mensajes

# Imprime la información general/resumida sobre el DataFrame de los mensajes
print(messages.info())

# Imprime una muestra de datos para los mensajes

print(messages.head())


# Basados en la primera observacion podemos necesitar los datos relacionados a fechas en formato "datetime", esto nos permitira su uso con los metodos correspondientes mas adelante 

# ### Corregir los datos

messages["message_date"] = pd.to_datetime(messages["message_date"], format="%Y-%m-%d")


# ### Enriquecer los datos

# In[112]:


messages["month"] = pd.to_datetime(messages["message_date"]).dt.to_period("M")
messages_per_month = (
    messages.groupby(["user_id", "month"])
    .size()
    .reset_index(name="messages_count")
)

print(messages_per_month.head())


# ## Internet

# Imprime la información general/resumida sobre el DataFrame de internet

print(internet.info())

# Imprime una muestra de datos para el tráfico de internet

print(internet.head())


# Basados en la primera observacion podemos necesitar los datos relacionados a fechas en formato "datetime", esto nos permitira su uso con los metodos correspondientes mas adelante 

# ### Corregir los datos

internet["session_date"] = pd.to_datetime(internet["session_date"], format="%Y-%m-%d")


# ### Enriquecer los datos

# In[178]:


internet = internet[internet["mb_used"] > 0]
internet["mb_used"] = pd.to_numeric(internet["mb_used"], errors="coerce")
# Regla 1: Todo consumo menor a 1 MB se convierte en 1 MB
internet["mb_used"] = np.where(internet["mb_used"] < 1, 1, internet["mb_used"])

# Regla 2: Redondeo hacia arriba para valores decimales
internet["usage_mb"] = np.ceil(internet["mb_used"])
internet = internet.dropna(subset=["user_id", "mb_used"])
internet["month"] = internet["session_date"].dt.to_period("M")
internet["usage_mb"] = np.ceil(internet["usage_mb"])
print(internet.head())


# ## Estudiar las condiciones de las tarifas

# In[117]:


# Imprime las condiciones de la tarifa y asegúrate de que te quedan claras

print(plans.info())
print(plans.head())


# ## Agregar datos por usuario
# 

# In[118]:


# Calcula el número de llamadas hechas por cada usuario al mes. Guarda el resultado.

calls_per_month = calls.groupby(["user_id", "call_date"]).agg({'duration': 'sum'}).reset_index()
calls_per_month.rename(columns={'duration': 'total_minutes'}, inplace=True)
calls_per_month['month'] = pd.to_datetime(calls_per_month['call_date']).dt.to_period('M')
print(calls_per_month.head())


# In[119]:


# Calcula la cantidad de minutos usados por cada usuario al mes. Guarda el resultado.

user_call_summary_by_date = (
    calls.groupby(["user_id", "call_date"])
    .agg(total_minutes=("duration", "sum"))
    .reset_index()
)
user_call_summary_by_date['month'] = pd.to_datetime(user_call_summary_by_date['call_date']).dt.to_period('M')
print(user_call_summary_by_date.head())


# In[130]:


# Calcula el número de mensajes enviados por cada usuario al mes. Guarda el resultado.



messages["month"] = pd.to_datetime(messages["message_date"]).dt.to_period("M")
messages_per_month = (
    messages.groupby(["user_id", "month"])
    .size()
    .reset_index(name="messages_count")
)

print(messages_per_month.head())


# In[131]:


# Calcula el volumen del tráfico de Internet usado por cada usuario al mes. Guarda el resultado.


internet_per_month = internet.groupby(["user_id", "session_date"]).agg({'usage_mb': 'sum'}).reset_index()
internet_per_month['month'] = pd.to_datetime(internet_per_month['session_date']).dt.to_period('M')
print(internet_per_month.head())


# In[132]:


# Fusiona los datos de llamadas, minutos, mensajes e Internet con base en user_id y month
summary_per_month = calls_per_month.merge(
    messages_per_month, on=["user_id", "month"], how="outer"
).merge(
    internet_per_month, on=["user_id", "month"], how="outer"
)
summary_per_month.fillna(0, inplace=True)
print(summary_per_month.head())


users['churn_date'] = users['churn_date'].replace(0, pd.NaT)
monthly_summary = summary_per_month.groupby(['user_id', 'month']).agg(
    total_minutes=('total_minutes', 'sum'),
    messages_count=('messages_count', 'sum'),
    usage_mb=('usage_mb', 'sum')
).reset_index()
summary_with_users = monthly_summary.merge(
    users[['user_id', 'plan', 'churn_date',"city"]], on='user_id', how='left'
)
summary_with_users.rename(columns={'plan': 'plan_name'}, inplace=True)
summary_with_plans = summary_with_users.merge(plans, on='plan_name', how='left')
summary_with_plans['extra_minutes'] = (
    summary_with_plans['total_minutes'] - summary_with_plans['minutes_included']
).clip(lower=0)

summary_with_plans['extra_messages'] = (
    summary_with_plans['messages_count'] - summary_with_plans['messages_included']
).clip(lower=0)

summary_with_plans['extra_mb'] = (
    summary_with_plans['usage_mb'] - summary_with_plans['mb_per_month_included']
).clip(lower=0)
summary_with_plans['extra_minute_cost'] = summary_with_plans['extra_minutes'] * summary_with_plans['usd_per_minute']
summary_with_plans['extra_message_cost'] = summary_with_plans['extra_messages'] * summary_with_plans['usd_per_message']
summary_with_plans['extra_mb_cost'] = (summary_with_plans['extra_mb'] / 1024) * summary_with_plans['usd_per_gb']
active_users_summary = summary_with_plans[summary_with_plans['churn_date'].isna()]
print("\nResumen final de usuarios activos:")
print(active_users_summary[['user_id', 'plan_name', 'total_minutes', 'messages_count', 
                            'usage_mb',"city"]].head())



summary_with_plans['total_minutes'] = summary_with_plans['total_minutes'].fillna(0)
summary_with_plans['messages_count'] = summary_with_plans['messages_count'].fillna(0)
summary_with_plans['usage_mb'] = summary_with_plans['usage_mb'].fillna(0)
summary_with_plans['extra_minutes'] = (
    summary_with_plans['total_minutes'] - summary_with_plans['minutes_included']
).clip(lower=0)

summary_with_plans['extra_messages'] = (
    summary_with_plans['messages_count'] - summary_with_plans['messages_included']
).clip(lower=0)

summary_with_plans['extra_mb'] = (
    summary_with_plans['usage_mb'] - summary_with_plans['mb_per_month_included']
).clip(lower=0)
summary_with_plans['extra_minute_cost'] = summary_with_plans['extra_minutes'] * summary_with_plans['usd_per_minute']
summary_with_plans['extra_message_cost'] = summary_with_plans['extra_messages'] * summary_with_plans['usd_per_message']
summary_with_plans['extra_mb_cost'] = (summary_with_plans['extra_mb'] / 1024) * summary_with_plans['usd_per_gb']
summary_with_plans['total_monthly_cost'] = (
    summary_with_plans['usd_monthly_pay'] +
    summary_with_plans['extra_minute_cost'] +
    summary_with_plans['extra_message_cost'] +
    summary_with_plans['extra_mb_cost']
)
monthly_revenue = summary_with_plans.groupby(['user_id', 'month']).agg(
    total_income=('total_monthly_cost', 'sum')
).reset_index()
print("\nIngresos mensuales por usuario:")
print(monthly_revenue.head())


# ## Estudia el comportamiento de usuario

# ### Llamadas

# In[135]:


# Compara la duración promedio de llamadas por cada plan y por cada mes. Traza un gráfico de barras para visualizarla.
summary_with_plans['total_minutes'] = summary_with_plans['total_minutes'].fillna(0)
avg_call_duration = (
    summary_with_plans.groupby(['month', 'plan_name'])
    .agg(avg_duration=('total_minutes', 'mean'))
    .reset_index()
)
plt.figure(figsize=(12, 6))
sns.barplot(data=avg_call_duration, x='month', y='avg_duration', hue='plan_name')
plt.title('Duración Promedio de Llamadas por Plan y Mes')
plt.xlabel('Mes')
plt.ylabel('Duración Promedio de Llamadas (Minutos)')
plt.xticks(rotation=45) 
plt.legend(title='Plan')
plt.tight_layout() 


plt.show()




summary_with_plans['total_minutes'] = summary_with_plans['total_minutes'].fillna(0).astype(float)
total_minutes_by_user = (
    summary_with_plans.groupby(['user_id', 'month', 'plan_name'])
    .agg(total_minutes=('total_minutes', 'sum'))
    .reset_index()
)

plt.figure(figsize=(12, 6))
sns.histplot(data=total_minutes_by_user, x='total_minutes', hue='plan_name', multiple='stack', bins=20)
plt.title('Distribución de Minutos Mensuales por Plan')
plt.xlabel('Total de Minutos Mensuales')
plt.ylabel('Frecuencia')
plt.legend(title='Plan')
plt.tight_layout()  


plt.show()




# Calcula la media y la varianza de la duración mensual de llamadas.

summary_stats = (
    summary_with_plans.groupby(['plan_name', 'month'])
    .agg(
        mean_minutes=('total_minutes', 'mean'),    # Media de minutos
        variance_minutes=('total_minutes', 'var')  # Varianza de minutos
    )
    .reset_index()
)
print(summary_stats)


# In[138]:


# Traza un diagrama de caja para visualizar la distribución de la duración mensual de llamadas


sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))
sns.boxplot(data=summary_with_plans, x='plan_name', y='total_minutes')
plt.title('Diagrama de Caja de Duración de Llamadas por Plan')
plt.xlabel('Plan')
plt.ylabel('Duración Total de Llamadas (minutos)')

plt.show()


# Por lo que podemos obsrvar los usuarios con el plan ultimate tiende a llamas con una mayor duracion 

# ### Mensajes

# In[139]:


# Comprara el número de mensajes que tienden a enviar cada mes los usuarios de cada plan

summary_with_plans['messages_count'] = summary_with_plans['messages_count'].fillna(0)
avg_messages_count = (
    summary_with_plans.groupby(['month', 'plan_name'])
    .agg(avg_messages=('messages_count', 'mean'))
    .reset_index()
)
plt.figure(figsize=(12, 6))
sns.barplot(data=avg_messages_count, x='month', y='avg_messages', hue='plan_name')
plt.title('Promedio de Mensajes por Plan y Mes')
plt.xlabel('Mes')
plt.ylabel('Promedio de Mensajes Enviados')
plt.xticks(rotation=45) 
plt.legend(title='Plan')
plt.tight_layout() 

plt.show()
print(messages.head())


# In[147]:


summary_stats = (
    summary_with_plans.groupby(['plan_name', 'month'])
    .agg(
        mean_messages=('messages_count', 'mean'),    # Media de minutos
        variance_messsages=('messages_count', 'var')  # Varianza de minutos
    )
    .reset_index()
)

sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))
sns.boxplot(data=summary_with_plans, x='plan_name', y='messages_count')
plt.title('Diagrama de Caja de Mensajes por Plan')
plt.xlabel('Plan')
plt.ylabel('Cantidad de Mensajes')

plt.show()

print(summary_stats)


# In[184]:


summary_with_plans['messages_count'] = summary_with_plans['messages_count'].fillna(0).astype(float)
total_minutes_by_user = (
    summary_with_plans.groupby(['user_id', 'month', 'plan_name'])
    .agg(total_minutes=('messages_count', 'sum'))
    .reset_index()
)

plt.figure(figsize=(12, 6))
sns.histplot(data=total_minutes_by_user, x='total_minutes', hue='plan_name', multiple='stack', bins=10)
plt.title('Distribución de Mensajes Mensuales por Plan')
plt.xlabel('Total de Mensajes Mensuales')
plt.ylabel('Frecuencia')
plt.legend(title='Plan')
plt.tight_layout()  


plt.show()


# En general los usuarios de el plan "ultimate" utilizan en mayor proporcion el servicio de mensajeria 

# ### Internet

# In[142]:


summary_with_plans['usage_mb'] = summary_with_plans['usage_mb'].fillna(0)
avg_internet = (
    summary_with_plans.groupby(['month', 'plan_name'])
    .agg(avg_messages=('usage_mb', 'mean'))
    .reset_index()
)
plt.figure(figsize=(12, 6))
sns.barplot(data=avg_internet, x='month', y='avg_messages', hue='plan_name')
plt.title('Promedio de MB por Plan y Mes')
plt.xlabel('Mes')
plt.ylabel('Promedio de MB usados')
plt.xticks(rotation=45) 
plt.legend(title='Plan')
plt.tight_layout() 

plt.show()


summary_with_plans['usage_mb'] = summary_with_plans['usage_mb'].fillna(0).astype(float)
total_minutes_by_user = (
    summary_with_plans.groupby(['user_id', 'month', 'plan_name'])
    .agg(total_minutes=('usage_mb', 'sum'))
    .reset_index()
)

plt.figure(figsize=(12, 6))
sns.histplot(data=total_minutes_by_user, x='total_minutes', hue='plan_name', multiple='stack', bins=20)
plt.title('Distribución de MB Mensuales por Plan')
plt.xlabel('Total de MB Mensuales')
plt.ylabel('Frecuencia')
plt.legend(title='Plan')
plt.tight_layout()  


plt.show()


summary_stats = (
    summary_with_plans.groupby(['plan_name', 'month'])
    .agg(
        mean_messages=('usage_mb', 'mean'),    # Media de minutos
        variance_messsages=('usage_mb', 'var')  # Varianza de minutos
    )
    .reset_index()
)

sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))
sns.boxplot(data=summary_with_plans, x='plan_name', y='usage_mb')
plt.title('Diagrama de Caja de MB por Plan')
plt.xlabel('Plan')
plt.ylabel('Cantidad de MB')

plt.show()

print(summary_stats)


# Parece que, en general, se encuentran muy cercanos los consumos de ambos grupos en fechas recientes. La tendencia de los usuarios "ultimate" en el pasado tendía a usar un poco más de datos en algunos momentos.

# ## Ingreso

data = summary_with_plans[['plan_name', 'total_monthly_cost']]
stats_per_plan = data.groupby('plan_name')['total_monthly_cost'].describe()
print("Estadísticas Descriptivas de los Ingresos Mensuales por Plan:")
print(stats_per_plan)

plt.figure(figsize=(10, 6))
sns.boxplot(data=summary_with_plans, x='plan_name', y='total_monthly_cost')
plt.title('Distribución de Ingresos Mensuales por Plan')
plt.xlabel('Plan')
plt.ylabel('Ingreso Mensual (USD)')
plt.show()



# Los servicios adicionales a los inclidos aumentan el ingreso que proporciona este plan 

# ## Prueba las hipótesis estadísticas

ultimate_income = summary_with_plans[summary_with_plans['plan_name'] == 'ultimate']['total_monthly_cost']
surf_income = summary_with_plans[summary_with_plans['plan_name'] == 'surf']['total_monthly_cost']
print(f"Ingreso medio - Ultimate: {ultimate_income.mean():.2f}")
print(f"Ingreso medio - Surf: {surf_income.mean():.2f}")
t_stat, p_value = stats.ttest_ind(ultimate_income, surf_income, equal_var=False)
print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.4f}")
if p_value < alpha:
    print("Rechazamos la hipótesis nula: Los ingresos promedio son significativamente diferentes.")
else:
    print("No podemos rechazar la hipótesis nula: No hay evidencia suficiente para afirmar que los ingresos promedio son diferentes.")


ny_nj_income = summary_with_plans[
    summary_with_plans['city'].str.contains('New York|Jersey', case=False, na=False)
]['usd_monthly_pay']

other_regions_income = summary_with_plans[
    ~summary_with_plans['city'].str.contains('New York|Jersey', case=False, na=False)
]['usd_monthly_pay']
print(f"Ingreso medio - NY-NJ: {ny_nj_income.mean():.2f}")
print(f"Ingreso medio - Otras regiones: {other_regions_income.mean():.2f}")
t_stat, p_value = stats.ttest_ind(ny_nj_income, other_regions_income, equal_var=False)
print(f"\nT-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.4f}")
alpha = 0.05  # Nivel de significancia
if p_value < alpha:
    print("Rechazamos la hipótesis nula: Los ingresos promedio son significativamente diferentes.")
else:
    print("No podemos rechazar la hipótesis nula: No hay evidencia suficiente para afirmar que los ingresos promedio son diferentes.")


# ## Conclusión general
# Podemos concluir que el plan que generará mayores ingresos para la empresa será el "sturf". A lo largo del proyecto, hemos observado que los consumos de ambos grupos están muy cercanos en fechas recientes. Sin embargo, es interesante notar que, en el pasado, los usuarios del plan "ultimate" tendían a utilizar un poco más de datos en ciertos momentos, lo que sugiere que hay oportunidades para optimizar ambos planes.
# 
# La forma en que se redondean los valores y los patrones de consumo de los usuarios del plan "sturf" están evolucionando y, según nuestras proyecciones, tenderán a igualarse con los usuarios que prefieren el pago de "ultimate". Esto indica que los consumidores están interesados en las características y beneficios que ofrece el plan "sturf", lo cual es una señal positiva para su adopción.
# 
# Uno de los factores más significativos que influye en la elección de los usuarios es el pago fijo mensual. Este modelo proporciona una previsibilidad financiera que muchos consumidores valoran, ya que les permite planificar su presupuesto sin sorpresas. Además, los beneficios adicionales que el plan "sturf" proporciona son atractivos y fomentan el uso de servicios complementarios. Este uso adicional de servicios puede no solo satisfacer mejor las necesidades de los usuarios, sino que también puede ayudar a la empresa a superar los ingresos generados por el plan "ultimate".
# 
# Dado este análisis, recomendaría que el departamento de mercadotecnia, mencionado al inicio de este proyecto, concentre sus esfuerzos en promover el plan "sturf". La estrategia de marketing podría enfocarse en resaltar los beneficios del pago fijo y la experiencia positiva de los usuarios actuales del plan. Implementar campañas de publicidad que destaquen testimonios de clientes satisfechos también podría ser una excelente forma de atraer nuevos usuarios.
# 
# Además, sería beneficioso realizar un seguimiento continuo de los patrones de consumo de ambos grupos para ajustar nuestras estrategias y mejorar constantemente la propuesta de valor de ambos planes. Al hacerlo, no solo maximizaremos los ingresos de la empresa, sino que también mejoraremos la satisfacción del cliente, lo que a largo plazo puede resultar en una mayor fidelización y en el crecimiento sostenible de la empresa.
# 
# 
