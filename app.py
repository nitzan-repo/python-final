import streamlit as st
import ec2_manager
import s3_manager
import route53_manager

# Page Configuration
st.set_page_config(page_title="Platform Management UI", page_icon="☁️", layout="wide")

st.title("☁️ AWS Platform Management Dashboard")
st.write("Manage AWS resources (EC2, S3, Route53) easily through an interactive web interface.")

# Sidebar Navigation
service = st.sidebar.selectbox("Select Service to Manage", ["EC2 Instances", "S3 Buckets", "Route53 DNS"])

# ==========================================
# --- EC2 MANAGEMENT SCREEN ---
# ==========================================
if service == "EC2 Instances":
    st.header("💻 EC2 Management")

    tab1, tab2, tab3 = st.tabs(["View & Create", "Start & Stop", "Update & Terminate"])

    with tab1:
        st.subheader("Create a New EC2 Instance")
        instance_type = st.selectbox("Select Instance Type", ["t3.micro", "t2.small"], key="ec2_type")
        if st.button("Create EC2 Instance"):
            try:
                active_instances = [i for i in ec2_manager.get_cli_instances() if
                                    i['State']['Name'] in ['running', 'pending']]
                if len(active_instances) >= 2:
                    st.error("Error: Hard cap reached! Cannot create more than 2 running instances.")
                else:
                    ami = ec2_manager.get_latest_ubuntu_ami()
                    res = ec2_manager.create_instance(ami, instance_type)
                    instance_id = res['Instances'][0]['InstanceId']
                    st.success(f"Success! Created instance ID: {instance_id}")
            except Exception as e:
                st.error(f"Failed to create instance: {e}")

        st.divider()
        st.subheader("CLI-Created Active Instances")
        if st.button("Refresh List"):
            instances = ec2_manager.get_cli_instances()
            if not instances:
                st.info("No CLI-created instances found.")
            else:
                for inst in instances:
                    st.write(
                        f"- **ID:** {inst['InstanceId']} | **State:** {inst['State']['Name']} | **Type:** {inst['InstanceType']}")

    with tab2:
        st.subheader("Instance State Control (Start / Stop)")
        inst_id_target = st.text_input("Instance ID", key="target_inst")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Instance"):
                if ec2_manager.is_cli_instance(inst_id_target):
                    ec2_manager.start_instance(inst_id_target)
                    st.success(f"Successfully started instance: {inst_id_target}")
                else:
                    st.error("Error: Access denied. Not created by this CLI.")
        with col2:
            if st.button("Stop Instance"):
                if ec2_manager.is_cli_instance(inst_id_target):
                    ec2_manager.stop_instance(inst_id_target)
                    st.success(f"Successfully stopped instance: {inst_id_target}")
                else:
                    st.error("Error: Access denied. Not created by this CLI.")

    with tab3:
        st.subheader("Update Instance Type or Terminate")
        up_id = st.text_input("Instance ID for Update/Termination", key="up_inst")
        new_type = st.selectbox("New Instance Type", ["t3.micro", "t2.small"], key="new_t")
        if st.button("Update Instance Type"):
            try:
                ec2_manager.update_instance_type(up_id, new_type)
                st.success(f"Successfully updated instance {up_id} to type {new_type}")
            except Exception as e:
                st.error(f"Failed: {e}")

        if st.button("Terminate Instance", type="primary"):
            try:
                ec2_manager.terminate_instance(up_id)
                st.success(f"Successfully terminated: {up_id}")
            except Exception as e:
                st.error(f"Failed: {e}")

# ==========================================
# --- S3 MANAGEMENT SCREEN ---
# ==========================================
elif service == "S3 Buckets":
    st.header("🪣 S3 Management")

    tab1, tab2, tab3 = st.tabs(["Create & View", "Upload & Delete Bucket", "View & Delete Files"])

    with tab1:
        st.subheader("Create a New S3 Bucket")
        bucket_name = st.text_input("Bucket Name (Must be globally unique)")
        visibility = st.radio("Visibility Level", ["private", "public"])

        if st.button("Create Bucket"):
            try:
                is_public = (visibility == 'public')
                s3_manager.create_bucket(bucket_name, is_public=is_public)
                st.success(f"Success! Created S3 bucket: {bucket_name} ({visibility})")
            except Exception as e:
                st.error(f"Failed: {e}")

        st.divider()
        st.subheader("CLI-Created Buckets")
        if st.button("Show Buckets"):
            buckets = s3_manager.get_cli_buckets()
            if not buckets:
                st.info("No CLI-created S3 buckets found.")
            else:
                for b in buckets:
                    st.write(f"- {b}")

    with tab2:
        st.subheader("Upload File to Bucket")
        up_bucket = st.text_input("Bucket Name", key="upload_bucket_input")
        uploaded_file = st.file_uploader("Choose a file to upload")

        if uploaded_file and st.button("Upload File"):
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            try:
                s3_manager.upload_file_to_bucket(up_bucket, uploaded_file.name)
                st.success(f"Successfully uploaded {uploaded_file.name} to {up_bucket}")
            except Exception as e:
                st.error(f"Failed: {e}")

        st.divider()
        st.subheader("Delete S3 Bucket")
        del_bucket_name = st.text_input("Bucket Name to Delete (Must be empty)", key="delete_bucket_input")
        if st.button("Delete Bucket", type="primary"):
            try:
                s3_manager.delete_bucket(del_bucket_name)
                st.success(f"Successfully deleted S3 bucket: {del_bucket_name}")
            except Exception as e:
                st.error(f"Failed: {e}")

    with tab3:
        st.subheader("View and Delete Files Inside a Bucket")
        target_bucket = st.text_input("Enter Bucket Name to List Files", key="files_bucket_input")

        if st.button("Fetch Files"):
            if not target_bucket.strip():
                st.error("Error: Please enter a valid S3 bucket name before fetching files.")
            else:
                try:
                    files = s3_manager.list_bucket_files(target_bucket)
                    st.session_state['current_bucket_files'] = files
                    st.session_state['active_files_bucket'] = target_bucket
                except Exception as e:
                    st.error(f"Failed to fetch files: {e}")

        if 'active_files_bucket' in st.session_state and st.session_state['active_files_bucket'] == target_bucket:
            files_list = st.session_state.get('current_bucket_files', [])
            if not files_list:
                st.info("The bucket is empty or no files found.")
            else:
                st.write(f"Files in **{target_bucket}**:")
                selected_file = st.selectbox("Select a file to delete", files_list)

                if st.button("Delete Selected File", type="primary"):
                    try:
                        s3_manager.delete_file_from_bucket(target_bucket, selected_file)
                        st.success(f"Successfully deleted file: {selected_file}")
                        st.session_state['current_bucket_files'] = s3_manager.list_bucket_files(target_bucket)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete file: {e}")

# ==========================================
# --- ROUTE53 MANAGEMENT SCREEN ---
# ==========================================
elif service == "Route53 DNS":
    st.header("🌐 Route53 DNS Management")

    tab1, tab2 = st.tabs(["Hosted Zones", "DNS Records"])

    with tab1:
        st.subheader("Create and Manage Hosted Zones")
        zone_name = st.text_input("Domain Name (e.g., nitzan.local.)")
        vpc_id_input = st.text_input("VPC ID (Optional - for Private Hosted Zone only)", value="")

        if st.button("Create Hosted Zone"):
            try:
                v_id = vpc_id_input if vpc_id_input.strip() else None
                zone_id = route53_manager.create_hosted_zone(zone_name, vpc_id=v_id)
                z_type = "Private" if v_id else "Public"
                st.success(f"Success! Created {z_type} Hosted Zone with ID: {zone_id}")
            except Exception as e:
                st.error(f"Failed: {e}")

        st.divider()
        if st.button("Show CLI Hosted Zones"):
            zones = route53_manager.list_cli_hosted_zones()
            if not zones:
                st.info("No CLI-created Hosted Zones found.")
            else:
                for z in zones:
                    st.write(f"- **ID:** {z['Id'].split('/')[-1]} | **Name:** {z['Name']}")

        del_z_id = st.text_input("Hosted Zone ID to Delete")
        if st.button("Delete Hosted Zone", type="primary"):
            try:
                route53_manager.delete_hosted_zone(del_z_id)
                st.success(f"Successfully deleted Hosted Zone: {del_z_id}")
            except Exception as e:
                st.error(f"Failed: {e}")

    with tab2:
        st.subheader("Manage DNS Records (Upsert / Delete)")
        rec_zone_id = st.text_input("Hosted Zone ID")
        rec_name = st.text_input("Record Name (e.g., www.nitzan.local.)")
        rec_type = st.selectbox("Record Type", ["A", "CNAME", "TXT"])
        rec_value = st.text_input("Record Value (IP/Target/Text)")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Upsert Record"):
                try:
                    route53_manager.upsert_record(rec_zone_id, rec_name, rec_type, rec_value)
                    st.success(f"Successfully upserted record {rec_name} ({rec_type})")
                except Exception as e:
                    st.error(f"Failed: {e}")
        with col2:
            if st.button("Delete Record", type="primary"):
                try:
                    route53_manager.delete_record(rec_zone_id, rec_name, rec_type, rec_value)
                    st.success(f"Successfully deleted record {rec_name}")
                except Exception as e:
                    st.error(f"Failed: {e}")