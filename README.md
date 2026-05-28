# Dashboard NPS · Claro Colombia

Dashboard interactivo para gestión NPS construido con Streamlit + Plotly.

## Requisitos

- Python 3.9 o superior
- El archivo `Gestion_NPS_-_Mayo.xlsx` en la misma carpeta que `app.py`

## Instalación (una sola vez)

```bash
pip install -r requirements.txt
```

## Correr el dashboard

```bash
streamlit run app.py
```

Se abre automáticamente en tu navegador en `http://localhost:8501`

## Actualizar datos

Solo reemplaza el archivo `Gestion_NPS_-_Mayo.xlsx` con la versión nueva
y haz clic en **Recargar datos** en la barra lateral — sin reiniciar nada.

## Compartir con tu jefe (gratis)

### Opción A — Streamlit Cloud (recomendado)
1. Sube el proyecto a GitHub (repo privado)
2. Ve a https://share.streamlit.io
3. Conecta el repo y despliega
4. Obtienes un link público tipo `https://tu-app.streamlit.app`

### Opción B — Red local
Si tu jefe está en la misma red, corre:
```bash
streamlit run app.py --server.address 0.0.0.0
```
Y comparte tu IP local: `http://TU_IP:8501`

## Filtros disponibles

- Mes actual
- Soporte / Agente
- Semanas (multiselect)
- Asignación (Atendida / Gestión)
- Tipo de red (FTTH / HFC)
- Zona geográfica

## Exportar

El botón **Exportar CSV filtrado** descarga exactamente los registros
que están visibles con los filtros aplicados.
