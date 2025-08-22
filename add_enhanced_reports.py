#!/usr/bin/env python3
"""
Add enhanced reports button to admin section
"""

def add_enhanced_reports():
    # Read the current main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the location to insert the enhanced reports button
    insertion_point = "    root.mainloop()"
    
    enhanced_reports_code = '''        
        # Row 4: Enhanced reporting
        row4_frame = tk.Frame(admin_frame, bg='#f0f0f0')
        row4_frame.pack(fill='x', pady=(10, 0))
        
        def show_enhanced_reports():
            """Show enhanced reporting dashboard"""
            from enhanced_features import show_enhanced_admin_reports
            show_enhanced_admin_reports(root, current_user)
        
        tk.Button(row4_frame, text="📊 Enhanced Reports Dashboard", command=show_enhanced_reports, 
                 bg='#8e44ad', fg='white', font=('Arial', 12, 'bold'), pady=12).pack(fill='x', padx=50)

    root.mainloop()'''
    
    if insertion_point in content:
        content = content.replace(insertion_point, enhanced_reports_code)
        print("✓ Added enhanced reports button to admin section")
    else:
        print("✗ Could not find insertion point for enhanced reports")
    
    # Write the enhanced main.py
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Enhanced reports added to main.py")

if __name__ == "__main__":
    add_enhanced_reports()