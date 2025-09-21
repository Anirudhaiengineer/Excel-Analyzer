import streamlit as st
import pandas as pd
import Excel   # your backend module
import uuid

st.title("📊 Excel Analysis Tool")

# Upload file
upload_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls", "csv"])
if upload_file is not None:
    # Load dataset
    if upload_file.name.endswith(".csv"):
        df = pd.read_csv(upload_file)
    else:
        df = pd.read_excel(upload_file, engine="openpyxl")

    st.write("### 🔍 Uploaded Data Preview")
    st.dataframe(df.head())

    st.session_state.df = df
    if "df" in st.session_state:
        df = st.session_state.df
        col_list = Excel.return_col(df)
        

        st.subheader("🧹 Remove Duplicates")
        selected_columns = st.multiselect(
            "Select columns to use as primary/unique keys",
            options=col_list,
            default=st.session_state.get("selected_columns", [])
        )
        st.session_state.selected_columns = selected_columns

        if st.button("Remove Duplicates"):
            if selected_columns:
                df = Excel.remove_duplicates(df, subset=selected_columns)
                st.session_state.df = df
                st.success("✅ Duplicates removed!")
            else:
                st.error("⚠️ Please select at least one column.")
        '''#replacing abbrevations
        st.subheader("🔍 Find Abbreviations")
        column_for_abbr = st.selectbox("Select column to find abbreviations", options=col_list)
        if st.button("Find Abbreviations"):
            abbrs = Excel.find_abbrevations(df, column_for_abbr)
        '''
        # -------------------------------
        # 2. Value Replacement
        # -------------------------------
        st.subheader("🔄 Replace Inconsistent Values")
        column_to_edit = st.selectbox("Choose a column to clean:", options=col_list)
        unique_vals = df[column_to_edit].dropna().unique().tolist()

        mapping = {}
        for val in unique_vals:
            new_val = st.text_input(f"Replace '{val}' with:", value=val, key=f"{column_to_edit}_{val}")
            if new_val != val:
                mapping[val] = new_val



        if st.button("Apply Replacements"):
            df = Excel.change_values(df, column_to_edit, mapping)
            st.session_state.df = df
            st.success(f"✅ Values updated in column '{column_to_edit}'")
        #Assign data type and range
        st.subheader("Data Columns and assign type and range")
        uuid_range = str(uuid.uuid4())[:8]
        col_key = f"column_to_set_range_{uuid_range}"
        if col_key in st.session_state:
            if st.session_state[col_key] not in col_list:
                st.session_state[col_key] = col_list[0]
        column_to_set_range = st.selectbox(
            "Choose a column to clean:", 
            options=col_list, 
            key=col_key
        )
        data_type = st.selectbox(
            "Select Data Type", 
            options=["int", "float", "str", "bool"], 
            key=f"data_type_{column_to_set_range}_{uuid_range}"
        )
        min_value = st.number_input(
            "Minimum Value", 
            value=0, 
            key=f"min_value_{column_to_set_range}_{uuid_range}"
        )
        max_value = st.number_input(
            "Maximum Value", 
            value=100, 
            key=f"max_value_{column_to_set_range}_{uuid_range}"
        )
        if st.button("Set Data Type and Range", key=f"set_dtype_range_{column_to_set_range}_{uuid_range}"):
            df[column_to_set_range] = Excel.set_datatype_and_range(df[column_to_set_range], data_type, (min_value, max_value))
            st.session_state.df = df
            st.success(f"✅ Data type set to {data_type} and range applied for column '{column_to_set_range}'")
        # -------------------------------
        # 3. Handle Nulls
        # -------------------------------
        st.subheader("🛠 Handle Null Values")
        for col in df.columns:
            skewness=Excel.set_skewness(df,col)
            st.write(f"Skewness of column '{col}': {skewness}")
        methods = {}
        for column in df.columns:
            if df[column].isnull().any()==True:
                if df[column].dtype in [float,int]:
                    if df[column].skew()>1 or df[column].skew()<-1:
                        methods[column] = st.radio(
                            f"Choose method for '{column}'",
                            options=["skip", "median", "mode", "drop","mean"],
                            index=0,
                            key=f"radio_{column}"
                        )
                    else:
                        methods[column] = st.radio(
                            f"Choose method for '{column}'",
                            options=["skip", "median", "mode", "drop","mean"],
                            index=4,
                            key=f"radio_{column}"
                        )  
                else:
                    methods[column] = st.radio(
                        f"Choose method for '{column}'",
                        options=["skip", "mode", "drop"],
                        index=0,
                        key=f"radio_{column}"
                    )                            

        if st.button("Handle Nulls"):
            df = Excel.handle_nulls(df, methods)
            st.session_state.df = df
            st.success("✅ Null values handled successfully")

        # -------------------------------
        # 4. Relations Between Columns
        # -------------------------------
        st.subheader("➕ Relation Between Columns")
        uid = str(uuid.uuid4())[:8]

        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            col_a = st.selectbox("Select Column 1", options=col_list, key=f"relation_col_a_{uid}")
        with col2:
            operation = st.selectbox("Select Operation", options=['+', '-', '*', '/', 'Concat'], key=f"relation_operation_{uid}")
        with col3:
            col_b = st.selectbox("Select Column 2", options=col_list, key=f"relation_col_b_{uid}")

        if st.button("Apply Operation", key=f"relation_apply_button_{uid}"):
            df = Excel.relation_btw_columns(df, col_a, col_b, operation)
            st.session_state.df = df
            st.success("✅ Operation applied successfully (new column added)")

        # -------------------------------
        # Final Preview
        # -------------------------------
        st.subheader("📑 Cleaned Data Preview")
        st.dataframe(df.head())

        # Download option
        st.download_button(
            label="⬇️ Download Cleaned Data",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="cleaned_data.csv",
            mime="text/csv"
        )


    
    
