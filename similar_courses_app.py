'''
To do's:
    - Add filter by semester
    - Display more information by course
    - Display information about the selected course
'''


import streamlit as st
import pandas as pd
import numpy as np

# Define the show_similars function
def show_similars(data, i, limit, display_info=False):
    """
    Display similar course IDs (and optionally names and descriptions) for a given course index.
    
    Args:
    - data: DataFrame containing the course data
    - i: Index of the specific course in the DataFrame
    - limit: Maximum number of elements to return
    - display_info: If True, display names and descriptions of similar courses
    
    Returns:
    - List of similar course IDs (and optionally names and descriptions) truncated to the specified limit
    """
    similar_ids = data.at[i, 'Similar_Course_Ids'][:limit]
    if display_info:
        similar_info = []
        for course_id in similar_ids:
            course_title = data.iloc[int(course_id)]['Course Title']
            course_description = data.iloc[int(course_id)]['Course Description']
            similar_info.append((course_id, course_title, course_description))
        return similar_info
    else:
        return similar_ids


# Load data (replace 'processed_data.csv' with your actual processed data file)
@st.cache_data
def load_data():
    return pd.read_pickle('processed_data.pkl')

def main():
    st.title('Similar Courses App')

    # Load data
    data = load_data()

    # Centered options
    col1, col2 = st.columns([1, 1])
    selected_course = col1.selectbox('Select a course:', data['Course Title'])
    limit = col2.slider('Max Number of Similar Courses', 1, 20, 10)

    # Find the index of the selected course
    try:
        selected_course_data = data[data['Course Title'] == selected_course].iloc[0]
        st.subheader(f'Selected course: {selected_course_data['Course Title']}')
        st.write(selected_course_data['Course Description'])
    except:
        st.warning('No results')
        
    i = data.index[data['Course Title'] == selected_course][0]
    
    # Show similar courses
    st.subheader('Similar Courses:')
    display_info = col1.checkbox('Display Names and Descriptions')
    similar_courses = show_similars(data, i, limit, display_info)
    if similar_courses is not None:
        for course_info in similar_courses:
            #print(f'course_info: {course_info}')
            if display_info:
                st.write(f"Course ID: {course_info[0]}")
                st.write(f"Course Title: {course_info[1]}")
                st.write(f"Course Description: {course_info[2]}")
                st.write('---')
            else:
                st.write(f"Course ID: {course_info}")

if __name__ == '__main__':
    main()
