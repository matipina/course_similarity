'''
To do's:
    - Group courses with same name (Figure out how to work with the different sections)
    - Display more information by course
    - Display information about the selected course
    - Add filter by semester
'''

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Course Recommender",
                   page_icon=":chart_with_upwards_trend:", layout="wide")

default_option = None


@st.cache_data
def load_data():
    data = pd.read_pickle('processed_data.pkl')
    # Group sections by course
    grouped_data = data.groupby(['Course Title', 'Term ', 'College', 'Campus',
                                'Department', 'Course Description', 'Schedule Type']).agg(lambda x: list(x)).reset_index()
    return data, grouped_data


def update_filters(option, value):
    """
    Update the selection state for a given filter option.

    Args:
    option (str): The name of the option being updated (e.g., 'College').
    value (str): The value selected by the user; reset to None if 'Select' is chosen.
    """
    # Update the selected option unless the default "Select" is chosen
    st.session_state['selected_filters'][option] = value if value != None else default_option
    # print(f'Updating S.S. with data: Option: {option}, Value: {value}')


def filter_data(data):
    """
    Filter the grouped data based on the selections stored in session state.

    Returns:
    DataFrame: The filtered data reflecting current selections.
    """
    print(f'Filtering data...')
    filtered_data = data.copy()
    # Apply filters based on current selections
    for key, value in st.session_state['selected_filters'].items():
        if value:
            filtered_data = filtered_data[filtered_data[key] == value]
    return filtered_data


# Filter data based on current selections
def filter_options(filter_column, data):
    conditions = {k: v for k, v in st.session_state['selected_filters'].items() if v and k != filter_column}
    filtered_data = data
    for cond_key, cond_value in conditions.items():
        filtered_data = filtered_data[filtered_data[cond_key] == cond_value]
    return np.insert(filtered_data[filter_column].unique(), 0, default_option)



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
            similar_info_dict = {}
            similar_info_dict['title'] = data.iloc[int(
                course_id)]['Course Title']
            similar_info_dict['crn'] = data.iloc[int(course_id)]['CRN']
            similar_info_dict['section'] = data.iloc[int(course_id)]['Section']
            similar_info_dict['college'] = data.iloc[int(course_id)]['College']
            similar_info_dict['campus'] = data.iloc[int(course_id)]['Campus']
            similar_info_dict['description'] = data.iloc[int(
                course_id)]['Course Description']
            similar_info_dict['department'] = data.iloc[int(
                course_id)]['Department']
            similar_info_dict['schedule'] = data.iloc[int(
                course_id)]['Schedule Type']
            similar_info_dict['faculty'] = data.iloc[int(
                course_id)]['Primary Faculty']
            similar_info.append(similar_info_dict)

        return similar_info
    else:
        return similar_ids


def main():
    st.title('Recommendation System for Similar Courses at The New School')

    st.write('The recommendation system has two main goals:')
    st.markdown(
        '- To guide students to similar courses when their desired courses are full.')
    st.markdown(
        '- To support academic leaders in identifying overlapping content in the curriculum to improve planning.')

    st.markdown('---')

    # Load data
    data, grouped_data = load_data()

    # Initialize session state for selectors
    if 'selected_filters' not in st.session_state:
        st.session_state['selected_filters'] = {
            'College': None,
            'Campus': None,
            'Department': None,
            'Schedule Type': None
        }

    # Centered options
    col1, col2 = st.columns([1, 1])
    
    college_options = np.insert(filter_data(grouped_data)[
                                "College"].unique(), 0, default_option)
    campus_options = np.insert(filter_data(grouped_data)[
                               "Campus"].unique(), 0, default_option)
    department_options = np.insert(filter_data(grouped_data)[
                                   "Department"].unique(), 0, default_option)
    schedule_options = np.insert(filter_data(grouped_data)[
                                 "Schedule Type"].unique(), 0, default_option)

    # all options are not changing right after the selection occurs
    selected_college = col1.selectbox('College:', college_options, index=college_options.tolist(
    ).index(st.session_state['selected_filters']['College']))
    selected_campus = col2.selectbox('Campus:', campus_options, index=campus_options.tolist(
    ).index(st.session_state['selected_filters']['Campus']))
    selected_department = col1.selectbox('Department:', department_options, index=department_options.tolist(
    ).index(st.session_state['selected_filters']['Department']))
    selected_schedule = col2.selectbox('Schedule Type:', schedule_options, index=schedule_options.tolist(
    ).index(st.session_state['selected_filters']["Schedule Type"]))

    update_filters('College', selected_college)
    update_filters('Campus', selected_campus)
    update_filters('Department', selected_department)
    update_filters('Schedule Type', selected_schedule)

    #st.write(st.session_state['selected_filters'])

    #st.write(f'College options: {college_options}')
    #st.write(f'Campus options: {campus_options}')
    #st.write(f'Selected college: {selected_college}')
    #st.write(f'Selected campus: {selected_campus}')
    #st.write(f'Selected department: {selected_department}')
    #st.write(f'Selected schedule: {selected_schedule}')

    # Course selector setup
    courses = np.insert(filter_data(grouped_data)[
                        "Course Title"].unique(), 0, default_option)
    selected_course = col1.selectbox('Select a course:', courses)

    # st.write(st.session_state['selected_filters'].items())

    # Find the index of the selected course
    try:
        selected_course_data = grouped_data[grouped_data['Course Title']
                                            == selected_course].iloc[0]
        with st.container(border=True):
            st.header(f'{selected_course_data["Course Title"]}', divider='red')
            st.write(f'{selected_course_data["College"]} | {selected_course_data["Department"]} | {selected_course_data["Campus"]}')
            st.write(f"Schedule type: **{selected_course_data['Schedule Type']}**")
            st.subheader('Description')
            st.write(selected_course_data['Course Description'])
    except:
        st.warning('No results')

    if len(data.index[data['Course Title'] == selected_course] > 0):
        i = data.index[data['Course Title'] == selected_course][0]

        # Show similar courses
        st.header('Similar Courses')
        limit = st.slider('Max Number of Similar Courses', 1, 20, 10)
        similar_courses = show_similars(data, i, limit, True)
        if similar_courses is not None:
            if len(similar_courses) > 0:
                i = 1
                for course_info in similar_courses:
                    with st.container(border=True):
                        st.header(f"{i}. {course_info['title']}")
                        st.write(f'{course_info["college"]} | {course_info["department"]} | {course_info["campus"]}')
                        st.write(f"Schedule type: **{course_info['schedule']}**")
                        with st.expander('Description', expanded=False):
                            st.write(f"{course_info['description']}")
                    i += 1
            else:
                st.warning('There are no similar courses.')
        else:
            st.error('Error: No similar courses found.')


if __name__ == '__main__':
    main()
