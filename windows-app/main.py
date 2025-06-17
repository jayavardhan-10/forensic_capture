import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, 
                             QPushButton, QComboBox, QLabel, QLineEdit, QMessageBox,
                             QGroupBox, QHBoxLayout, QRadioButton, QCheckBox)
from PyQt5.QtCore import Qt
from automation.facebook_automation import FacebookAutomation
from automation.instagram_automation import InstagramAutomation
from automation.reddit_automation import RedditAutomation
from automation.mastodon_automation import MastodonAutomation
from reports.report_generator import ReportGenerator
import os

class SocialMediaEvidenceTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Social Media Evidence Tool")
        self.setGeometry(100, 100, 1000, 800)
        
        self.facebook_automation = None
        self.instagram_automation = None
        self.reddit_automation = None
        self.mastodon_automation = None
        self.report_generator = ReportGenerator()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # Add margins and spacing for better layout
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Platform Selection Group
        platform_group = QGroupBox("Platform Selection")
        platform_layout = QVBoxLayout()
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Facebook", "Twitter", "Instagram", "Reddit", "Mastodon"])
        self.platform_combo.currentTextChanged.connect(self.on_platform_changed)
        platform_layout.addWidget(QLabel("Select Platform:"))
        platform_layout.addWidget(self.platform_combo)
        platform_group.setLayout(platform_layout)
        main_layout.addWidget(platform_group)
        
        # Extraction Method Group
        method_group = QGroupBox("Extraction Method")
        method_layout = QVBoxLayout()
        self.public_radio = QRadioButton("Public Profile (Using ID/Username)")
        self.authorized_radio = QRadioButton("Authorized Access (Using Credentials)")
        self.public_radio.setChecked(True)
        method_layout.addWidget(self.public_radio)
        method_layout.addWidget(self.authorized_radio)
        method_group.setLayout(method_layout)
        main_layout.addWidget(method_group)
        
        # Input Group
        input_group = QGroupBox("Account Information")
        input_layout = QFormLayout()
        # Public Profile Inputs
        self.profile_id_label = QLabel("Profile ID/Username:")
        self.profile_id_input = QLineEdit()
        input_layout.addRow(self.profile_id_label, self.profile_id_input)
        # Authorized Access Inputs
        self.username_label = QLabel("Username/Email:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.target_profile_label = QLabel("Target Profile ID/Username (default: me):")
        self.target_profile_input = QLineEdit()
        self.target_profile_input.setText("me")
        input_layout.addRow(self.username_label, self.username_input)
        input_layout.addRow(self.password_label, self.password_input)
        input_layout.addRow(self.target_profile_label, self.target_profile_input)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Data Selection Group
        data_group = QGroupBox("Data to Extract")
        data_layout = QVBoxLayout()
        self.data_combo = QComboBox()
        self.data_combo.addItems([
            "Posts",
            "Messages",
            "Timeline",
            "Friends List",
            "Account Info"
        ])
        data_layout.addWidget(QLabel("Select Data Type:"))
        data_layout.addWidget(self.data_combo)
        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)
        
        # Output Options Group
        output_group = QGroupBox("Output Options")
        output_layout = QVBoxLayout()
        self.save_as_pdf_checkbox = QCheckBox("Save as PDF Report")
        self.save_as_pdf_checkbox.setChecked(False)
        output_layout.addWidget(self.save_as_pdf_checkbox)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.extract_button = QPushButton("Extract Data")
        self.extract_button.clicked.connect(self.extract_data)
        self.extract_button.setMinimumHeight(40)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_inputs)
        self.clear_button.setMinimumHeight(40)
        button_layout.addWidget(self.extract_button)
        button_layout.addWidget(self.clear_button)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        self.public_radio.toggled.connect(self.toggle_input_fields)
        self.authorized_radio.toggled.connect(self.toggle_input_fields)
        self.toggle_input_fields()
        
        # Apply custom style sheet for a cleaner UI
        self.setStyleSheet("""
        QMainWindow { background-color: #f9f9f9; }
        QGroupBox { font-weight: bold; border: 1px solid #cccccc; border-radius: 5px; margin-top: 10px; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }
        QPushButton { background-color: #007ACC; color: white; border-radius: 5px; padding: 8px 16px; }
        QPushButton:hover { background-color: #005EA6; }
        QComboBox, QLineEdit { padding: 4px; border: 1px solid #999; border-radius: 3px; }
        """)

    def toggle_input_fields(self):
        is_public = self.public_radio.isChecked()
        self.profile_id_label.setVisible(is_public)
        self.profile_id_input.setVisible(is_public)
        self.username_label.setVisible(not is_public)
        self.username_input.setVisible(not is_public)
        self.password_label.setVisible(not is_public)
        self.password_input.setVisible(not is_public)
        self.target_profile_label.setVisible(not is_public)
        self.target_profile_input.setVisible(not is_public)
        
    def on_platform_changed(self, platform):
        self.data_combo.clear()
        if platform in ["Facebook", "Instagram"]:
            self.data_combo.addItems([
                "Posts",
                "Messages",
                "Timeline",
                "Friends List",
                "Account Info"
            ])
        elif platform == "Twitter":
            self.data_combo.addItems([
                "Tweets",
                "Timeline",
                "Account Info"
            ])
        elif platform == "Reddit":
            self.data_combo.addItems([
                "User Profile",
                "User Posts",
                "Subreddit"
            ])
        elif platform == "Mastodon":
            self.data_combo.addItems([
                "User Profile",
                "User Posts",
                "Hashtag"
            ])
            
    def clear_inputs(self):
        self.profile_id_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.target_profile_input.setText("me")
        self.data_combo.setCurrentIndex(0)
        
    def _generate_pdf_if_requested(self, platform, username, data_type, screenshot_paths):
        """Generate PDF report if the checkbox is selected"""
        if self.save_as_pdf_checkbox.isChecked():
            try:                # Ensure screenshot_paths is a list
                if isinstance(screenshot_paths, str):
                    screenshot_paths = [screenshot_paths]
                elif isinstance(screenshot_paths, dict):
                    # Extract all screenshots from the result dict
                    paths = []
                    
                    # First, handle the profile screenshot (always want this first)
                    if "profile" in screenshot_paths and isinstance(screenshot_paths["profile"], str):
                        paths.append(screenshot_paths["profile"])
                    
                    # Next, check for posts_all which contains all post screenshots
                    if "posts_all" in screenshot_paths and isinstance(screenshot_paths["posts_all"], list):
                        paths.extend(screenshot_paths["posts_all"])
                    
                    # Next, check for numbered posts (posts_1, posts_2, etc.)
                    for i in range(1, 10):  # Look for up to 10 numbered posts
                        key = f"posts_{i}"
                        if key in screenshot_paths and isinstance(screenshot_paths[key], str):
                            paths.append(screenshot_paths[key])
                    
                    # Finally, add any other string values that might be screenshots
                    for key, value in screenshot_paths.items():
                        if isinstance(value, str) and key not in ["profile", "metadata"] and not key.startswith("posts_"):
                            paths.append(value)
                            
                    screenshot_paths = paths
                
                # Filter out None values, ensure files exist, and only include image files
                valid_screenshots = []
                image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
                
                for path in screenshot_paths:
                    if path and os.path.exists(path):
                        # Check if the file has an image extension
                        _, ext = os.path.splitext(path.lower())
                        if ext in image_extensions:
                            valid_screenshots.append(path)
                
                if valid_screenshots:
                    pdf_path = self.report_generator.generate_report(platform, username, data_type, valid_screenshots)
                    return pdf_path
                else:
                    QMessageBox.warning(self, "PDF Warning", "No valid screenshot images found to include in PDF")
                    return None
            except Exception as e:
                QMessageBox.warning(self, "PDF Error", f"Failed to generate PDF: {str(e)}")
                return None
        return None
        
    def extract_data(self):
        platform = self.platform_combo.currentText()
        data_type = self.data_combo.currentText()
        
        try:
            if platform == "Facebook":
                if self.public_radio.isChecked():
                    profile_id = self.profile_id_input.text()
                    if not profile_id:
                        QMessageBox.warning(self, "Error", "Please enter a Profile ID/Username")
                        return
                    
                    if not self.facebook_automation:
                        self.facebook_automation = FacebookAutomation()
                    
                    screenshot_path = self.facebook_automation.extract_public_profile(profile_id, data_type)
                    if screenshot_path:
                        # Generate PDF if requested
                        pdf_path = self._generate_pdf_if_requested(platform, profile_id, data_type, screenshot_path)
                        
                        if pdf_path:
                            QMessageBox.information(self, "Success", f"Data extracted successfully!\nScreenshot: {screenshot_path}\nPDF Report: {pdf_path}")
                        else:
                            QMessageBox.information(self, "Success", f"Data extracted successfully!\nSaved to: {screenshot_path}")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to extract data")
                else:
                    username = self.username_input.text()
                    password = self.password_input.text()
                    target_profile = self.target_profile_input.text() or "me"
                    
                    if not username or not password:
                        QMessageBox.warning(self, "Error", "Please enter both username and password")
                        return
                    
                    if not target_profile:
                        QMessageBox.warning(self, "Error", "Please enter a Target Profile ID/Username")
                        return
                    
                    if not self.facebook_automation:
                        self.facebook_automation = FacebookAutomation()
                    
                    if self.facebook_automation.login(username, password):
                        screenshot_path = self.facebook_automation.extract_authorized_data(data_type, target_profile)
                        if screenshot_path:
                            # Generate PDF if requested
                            pdf_path = self._generate_pdf_if_requested(platform, target_profile, data_type, screenshot_path)
                            
                            if pdf_path:
                                QMessageBox.information(self, "Success", f"Data extracted successfully!\nScreenshot: {screenshot_path}\nPDF Report: {pdf_path}")
                            else:
                                QMessageBox.information(self, "Success", f"Data extracted successfully!\nSaved to: {screenshot_path}")
                        else:
                            QMessageBox.warning(self, "Error", "Failed to extract data")
                    else:
                        QMessageBox.warning(self, "Error", "Login failed")
            
            elif platform == "Twitter":
                QMessageBox.information(self, "Info", "Twitter functionality is not yet implemented")
                return
            
            elif platform == "Instagram":
                if self.public_radio.isChecked():
                    profile_id = self.profile_id_input.text()
                    if not profile_id:
                        QMessageBox.warning(self, "Error", "Please enter a Profile ID/Username")
                        return
                    
                    if not self.instagram_automation:
                        self.instagram_automation = InstagramAutomation()
                    
                    screenshot_path = self.instagram_automation.extract_public_profile(profile_id, data_type)
                    if screenshot_path:
                        # Generate PDF if requested
                        pdf_path = self._generate_pdf_if_requested(platform, profile_id, data_type, screenshot_path)
                        
                        if pdf_path:
                            QMessageBox.information(self, "Success", f"Data extracted successfully!\nScreenshot: {screenshot_path}\nPDF Report: {pdf_path}")
                        else:
                            QMessageBox.information(self, "Success", f"Data extracted successfully!\nSaved to: {screenshot_path}")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to extract data")
                else:
                    username = self.username_input.text()
                    password = self.password_input.text()
                    target_profile = self.target_profile_input.text() or "me"
                    
                    if not username or not password:
                        QMessageBox.warning(self, "Error", "Please enter both username and password")
                        return
                    
                    if not target_profile:
                        QMessageBox.warning(self, "Error", "Please enter a Target Profile ID/Username")
                        return
                    
                    if not self.instagram_automation:
                        self.instagram_automation = InstagramAutomation()
                    
                    if self.instagram_automation.login(username, password):
                        screenshot_path = self.instagram_automation.extract_authorized_data(data_type, target_profile)
                        if screenshot_path:
                            # Generate PDF if requested
                            pdf_path = self._generate_pdf_if_requested(platform, target_profile, data_type, screenshot_path)
                            
                            if pdf_path:
                                QMessageBox.information(self, "Success", f"Data extracted successfully!\nScreenshot: {screenshot_path}\nPDF Report: {pdf_path}")
                            else:
                                QMessageBox.information(self, "Success", f"Data extracted successfully!\nSaved to: {screenshot_path}")
                        else:
                            QMessageBox.warning(self, "Error", "Failed to extract data")
                    else:
                        QMessageBox.warning(self, "Error", "Login failed")
            
            elif platform == "Reddit":
                if self.public_radio.isChecked():
                    username = self.profile_id_input.text()
                    if not username:
                        QMessageBox.warning(self, "Error", "Please enter a Reddit Username")
                        return
                    
                    if not self.reddit_automation:
                        self.reddit_automation = RedditAutomation()
                    
                    data_type = self.data_combo.currentText()
                    if data_type == "User Profile" or data_type == "User Posts":
                        result = self.reddit_automation.extract_public_profile(username)
                        if result:
                            # Generate PDF if requested
                            pdf_path = self._generate_pdf_if_requested(platform, username, data_type, result)
                            
                            if pdf_path:
                                QMessageBox.information(self, "Success", f"Data extracted successfully!\nProfile screenshot: {result['profile']}\nPosts screenshot: {result['posts']}\nPDF Report: {pdf_path}")
                            else:
                                QMessageBox.information(self, "Success", f"Data extracted successfully!\nProfile screenshot: {result['profile']}\nPosts screenshot: {result['posts']}")
                        else:
                            QMessageBox.warning(self, "Error", "Failed to extract data from Reddit")
                    elif data_type == "Subreddit":
                        result = self.reddit_automation.extract_subreddit(username)
                        if result:
                            # Generate PDF if requested
                            pdf_path = self._generate_pdf_if_requested(platform, username, data_type, result)
                            
                            if pdf_path:
                                QMessageBox.information(self, "Success", f"Data extracted successfully!\nSubreddit screenshot: {result['subreddit']}\nPosts screenshot: {result['posts']}\nPDF Report: {pdf_path}")
                            else:
                                QMessageBox.information(self, "Success", f"Data extracted successfully!\nSubreddit screenshot: {result['subreddit']}\nPosts screenshot: {result['posts']}")
                        else:
                            QMessageBox.warning(self, "Error", "Failed to extract data from Reddit")
                    else:
                        QMessageBox.warning(self, "Error", "This data type is not yet implemented for Reddit")
                        return
                else:
                    QMessageBox.information(self, "Info", "Reddit only supports public profile extraction. Please select 'Public Profile' option.")
                    return
            
            elif platform == "Mastodon":
                if self.public_radio.isChecked():
                    username = self.profile_id_input.text()
                    if not username:
                        QMessageBox.warning(self, "Error", "Please enter a Mastodon Username")
                        return
                    
                    # Additional input for Mastodon instance
                    instance = "mastodon.social"  # Default instance
                    
                    if not self.mastodon_automation:
                        self.mastodon_automation = MastodonAutomation()
                    
                    data_type = self.data_combo.currentText()
                    if data_type == "User Profile" or data_type == "User Posts":
                        result = self.mastodon_automation.extract_public_profile(username, instance)
                    elif data_type == "Hashtag":
                        result = self.mastodon_automation.extract_hashtag(username, instance)
                    else:
                        QMessageBox.warning(self, "Error", "This data type is not yet implemented for Mastodon")
                        return
                    
                    if result:
                        # Generate PDF if requested
                        pdf_path = self._generate_pdf_if_requested(platform, username, data_type, result)
                        
                        if pdf_path:
                            QMessageBox.information(self, "Success", f"Data extracted successfully!\nProfile screenshot: {result['profile']}\nPosts screenshot: {result['posts']}\nPDF Report: {pdf_path}")
                        else:
                            QMessageBox.information(self, "Success", f"Data extracted successfully!\nProfile screenshot: {result['profile']}\nPosts screenshot: {result['posts']}")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to extract data from Mastodon")
                else:
                    QMessageBox.information(self, "Info", "Mastodon only supports public profile extraction. Please select 'Public Profile' option.")
                    return
                    
            else:
                QMessageBox.information(self, "Info", f"{platform} functionality is not yet implemented")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def closeEvent(self, event):
        if self.facebook_automation:
            self.facebook_automation.close()
        if self.instagram_automation:
            self.instagram_automation.close()
        event.accept()
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SocialMediaEvidenceTool()
    window.show()
    # Handle both PyQt5 (exec_) and newer versions (exec)
    try:
        sys.exit(app.exec())
    except AttributeError:
        sys.exit(app.exec_())
