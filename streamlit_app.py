# Import python packages
import streamlit as st
import requests
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the Fruit you want in your Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be", name_on_order)

# Snowflake session
#session = get_active_session()
cnx=st.connection("snowflake")
session=cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#convert the snowpark dataframe to a pandas dataframe so we can use the LOC function
pd_df=my_dataframe.to_pandas()
st.dataframe(pd_df)
#st.stop()

# Convert to list
fruit_list = my_dataframe.collect()
fruit_options = [row['FRUIT_NAME'] for row in fruit_list]

# Multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options
    ,max_selections=5
)
fruit_map = {
    "Apples": "Apple",
    "Blueberries": "Blueberry"
}

for fruit_chosen in ingredients_list:
    fruit_choice = fruit_map.get(fruit_chosen, fruit_chosen.rstrip('s'))
     st.subheader(fruit_chosen + ' Nutrition Information')
    fruityvice_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_choice.lower())
    
    if fruityvice_response.status_code == 200:
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
    else:
        st.error(f"Sorry, {fruit_chosen} is not available in the API database.")
# Display chosen ingredients
#1111if ingredients_list:
    #1111ingredients_string = ' '#.join(ingredients_list)

   #111 for fruit_chosen in ingredients_list:
    # 111   ingredients_string += fruit_chosen + ''

      #111  search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
      #11  st.subheader(fruit_chosen + 'Nutrition Information')
        #11fruityvice_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        #11fv_df=st.dataframe(data=fruityvice_response.json(),use_container_width=True)
        #smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon" + fruit_chosen)
        #sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

        

    # Build SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Debugging display
    st.write(my_insert_stmt)

    # Submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}! 🥤', icon="✅")

