url_data = 'Employees.csv'

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title='DSA05 EDUARDO', 
    page_icon=':star')

# 06. Crear título de la aplicación, encabezados y texto de descripción 
# del proyecto. 
st.title('Análisis de deserción de empleados')
st.write('Este tablero pretende analizar en lo general la información '\
         'obtenida de un grupo de empleados de una organización y '\
         'el factor de deserción laboral que cobra relevancia en la '\
         'actualidad en las empresas y organizaciones.') 

@st.cache
def leer_datos():
    datos = pd.read_csv(url_data)
    return datos

employees = leer_datos()

@st.cache
def buscar_texto(texto):
    return employees[employees[['Employee_ID', 'Hometown','Unit']].apply(
                    lambda row: row.astype(str).str.upper().str.contains(
                        texto.upper()).any(),
                    axis=1)]

@st.cache
def nivel_educativo(texto):
    return employees[
        employees['Education_Level'].astype(str).str.contains(str(texto))]

@st.cache
def ciudades(texto):
    return employees[
        employees['Hometown'].astype(str).str.contains(str(texto))]   

@st.cache
def unidades(texto):
    return employees[
        employees['Unit'].astype(str).str.contains(str(texto))]   


# 07. Crear un sidebar en la aplicación 
sb = st.sidebar

# Crear dos contenedores uno enfocado en mostrar los gráficos estadísticos 
# y otro en mostrar la tabla de datos 
cTabla = st.container()
cDashboard = st.container()

# Funcionalidades de SIDEBAR

# 08. En sidebar crear un control checkbox que permita mostrar u ocultar 
# el dataframe completo en el contenedor cTabla.
btmostrar = sb.checkbox('Mostrar los datos.')

# 09. Crear un buscador de empleados con cajas de texto y botones de comando, que 
# permitan buscar por Employee_ID, Hometown o Unit, mostrar dataframe con  
# resultados encontrados y total de empleados. Nota:  Usar funciones con cache. 
#sb.header('Buscar empleado por:')

texto = sb.text_input('Buscar:',
                      help='Buscar por ID de empelado, Ciudad o Unidad')
if (sb.button('Buscar') or texto):
    encontrado = buscar_texto(texto)
    if encontrado.empty:
        sb.warning('No se encontró el texto buscado.')
    else:
        employees = encontrado
    
# 10. En el sidebar incluir un control selectedbox que permita filtrar los 
# empleados por su nivel educativo, mostrar el dataframe filtrado y total 
# de empleados. Nota:  Usar funciones con cache. 

nv_eduativo = (*['-todos-'],*np.sort(leer_datos()['Education_Level'].unique()))
nvEducativo = sb.selectbox('Nivel educativo',nv_eduativo)
if(nvEducativo != '-todos-'):
    employees = nivel_educativo(nvEducativo)

# 11. En el sidebar crear un control selectedbox con las ciudades que participaron
# en el estudio, mostrar los empleados por ciudad en un dataframe filtrado y 
# total de empleados. Nota:  Usar funciones con cache. 

cd_participantes = (*['-todos-'],*np.sort(leer_datos()['Hometown'].unique()))
cdParticipantes =  sb.selectbox('Ciudades participantes',cd_participantes)
if(cdParticipantes != '-todos-'):
    employees = ciudades(cdParticipantes)

# 12. Crear un selectedbox para filtrar por la unidad funcional (Unit) a la que 
# pertenece. Nota: Usar funciones con cache. 

u_funcional = (*['-todos-'],*np.sort(leer_datos()['Unit'].unique()))
uFuncionales = sb.selectbox('Unidad Funcional',u_funcional)
if(uFuncionales != '-todos-'):
    employees = unidades(uFuncionales)

# Se muestra total de observables seleccionado.
observaciones = employees.shape[0]
sb.markdown(f'Total de observables: **{observaciones:,}**.')

with cTabla:

    if(btmostrar):
        st.markdown('*Tabla de datos:*')
        tbShow = employees.reset_index(drop=True).fillna('[empty]').astype('str')
        tbShow.index+=1
        st.dataframe(tbShow)

with cDashboard:
    st.write('----')   
    # 13. Crear un histograma de los empleados agrupados por edad. 
    fig1, ax1= plt.subplots()
    bin = np.arange((employees['Age'].min()//5)*5,
                    ((employees['Age'].max()//5)+1)*5,5)
    ax1.hist(employees['Age'].dropna(),bins=bin)
    ax1.set_title('Histograma de Edades ')
    ax1.set_xlabel('edad en quinqueneso')
    st.pyplot(fig1)

    st.write('----')    
    # 14. Gráfico de total de empleados por Unidad.
    fig2, ax2 = plt.subplots()
    te_unidad = employees[['Unit','Employee_ID']].groupby(
                    by=['Unit']).count().sort_values(
                        by=['Employee_ID'],
                            ascending=True)
    ax2.barh(te_unidad.index,te_unidad['Employee_ID'])
    ax2.set_title('Total de empleado por unidad \n(Unit)')
    ax2.set_xlabel('Empleados')
    ax2.set_ylabel('Unidades')
    st.pyplot(fig2)
    
    st.write('----')  
    # 15. Ciudades con mayor índice de deserción (Attrition_rate)
    # para este punto se seleccionó boxplot, qu epermite visualizar 
    # el comportamiento de cada grupo de datos.
    
    temp1 = employees[['Attrition_rate','Hometown']].groupby(
        by=['Hometown']).max()
    indice = temp1.max()[0]
    ciudad = temp1[temp1['Attrition_rate']==indice].index[0]
    st.markdown(f'La ciudad de **{ciudad}** tiene el tasa de deserción'\
                f' más grande, con **{indice}**.')
    fig3, ax3 = plt.subplots()
    employees[['Attrition_rate','Hometown']].groupby(by=['Hometown']).boxplot(
        ax=ax3,
        subplots=False,
        figsize=(5,15),
        sym='k+',
        vert=False)
    ax3.set_title('Ciudades y tasas de deserción')
    ax3.set_xlabel('Tasa de deserción')
    st.pyplot(fig3)
    
    st.write('----')   
    # 16. Grafico de dispersión de edades y tasa de deserción. (scatterplot)
    # 17. Grafico de dispersión de tiempo de servicio y tasa de deserción. (scatter plot)
    
    # Para este últimos dos puntos se usan gráficos de dispersión a fin de 
    # identificar correlación entre las variables observadas.

    #iniciar un subplots
    fig4, axs = plt.subplots(1,2,figsize=(10,5),squeeze=False)
    
    # Se usar el metodos plot.scatter desde Pandas especificando las variables x, y 
    # y el ax
    employees.plot.scatter(x='Attrition_rate', 
                           y='Age', ax=axs[0,0],
                           title= 'Edad Vs. Tasa de deserción',
                           fontsize=12)
    axs[0,0].set_xlabel('Tasa de deserción')
    axs[0,0].set_ylabel('Edad')
    # Se usar el metodos plot.scatter desde Pandas especificando las variables x, y 
    # y el ax
    employees.plot.scatter(x='Attrition_rate', 
                           y='Time_of_service', 
                           ax=axs[0,1],
                           title= 'Tiempo de Servicio Vs. Tasa de deserción',
                           fontsize=12)
    axs[0,1].set_xlabel('Tasa de deserción')
    axs[0,1].set_ylabel('Tiempo de Servicio')
    st.pyplot(fig4)
