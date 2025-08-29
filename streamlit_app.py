# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the Fruit you want in your Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be", name_on_order)

# Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to pandas
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

# Convert to list
fruit_list = my_dataframe.collect()
fruit_options = [row['FRUIT_NAME'] for row in fruit_list]

# Multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

# Map plurals to singular API names
fruit_map = {
    "Apples": "Apple",
    "Blueberries": "Blueberry",
    "Strawberries": "Strawberry",
    "Raspberries": "Raspberry",
    "Figs":"Figs",
    "Dragon Fruit":"Dragon Fruit"
}

# Show nutrition for each chosen fruit
for fruit_chosen in ingredients_list:
    fruit_choice = fruit_map.get(fruit_chosen, fruit_chosen.rstrip('s'))  # fix plurals
    st.subheader(fruit_chosen + ' Nutrition Information')
    fruityvice_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_choice.lower())
    
    if fruityvice_response.status_code == 200:
        fv_json = fruityvice_response.json()
        st.dataframe(data=fv_json, use_container_width=True)
    else:
        st.error(f"Sorry, {fruit_chosen} is not available in the API database.")

# --- Build ingredients string for insert ---
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    
    # Build SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write("SQL to be executed:")
    st.code(my_insert_stmt, language="sql")

    # Submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}! 🥤', icon="✅")
