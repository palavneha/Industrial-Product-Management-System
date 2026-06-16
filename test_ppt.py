from app import app
with app.app_context():
    from app import generate_service_ppt, generate_all_services_ppt, generate_manufacturing_ppt, generate_all_manufacturing_ppt
    
    print("Testing generate_service_ppt(1)")
    try:
        generate_service_ppt(1)
        print("Success for service 1")
    except Exception as e:
        print(f"Error for service 1: {e}")

    print("Testing generate_manufacturing_ppt(1)")
    try:
        generate_manufacturing_ppt(1)
        print("Success for manufacturing 1")
    except Exception as e:
        print(f"Error for manufacturing 1: {e}")
        
    print("Testing generate_all_services_ppt()")
    try:
        generate_all_services_ppt()
        print("Success for all services")
    except Exception as e:
        print(f"Error for all services: {e}")

    print("Testing generate_all_manufacturing_ppt()")
    try:
        generate_all_manufacturing_ppt()
        print("Success for all manufacturing")
    except Exception as e:
        print(f"Error for all manufacturing: {e}")
