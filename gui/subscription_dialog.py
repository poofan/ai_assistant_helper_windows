"""
Subscription Dialog - Modern subscription and payment interface using CustomTkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import webbrowser
import logging
from pathlib import Path

class SubscriptionDialog(ctk.CTkToplevel):
    """Modern subscription and payment dialog using CustomTkinter"""
    
    def __init__(self, parent, subscription_status, available_plans, credit_packages, purchase_url):
        super().__init__(parent)
        
        self.subscription_status = subscription_status
        self.available_plans = available_plans
        self.credit_packages = credit_packages
        self.purchase_url = purchase_url
        self.logger = logging.getLogger(__name__)
        self.result = None
        
        # Setup dialog
        self.setup_dialog()
        self.create_widgets()
        
        # Center the dialog
        self.center_dialog()
    
    def setup_dialog(self):
        """Setup dialog properties"""
        self.title("🔐 Подписка и оплата")
        self.geometry("700x600")
        self.resizable(True, True)
        self.minsize(600, 500)
        
        # Make dialog modal
        self.transient(self.master)
        self.grab_set()
        
        # Set dialog icon
        try:
            icon_path = Path("images") / "logo.png"
            if icon_path.exists():
                icon_image = tk.PhotoImage(file=str(icon_path))
                self.iconphoto(True, icon_image)
        except Exception as e:
            self.logger.error(f"Failed to load dialog icon: {e}")
    
    def center_dialog(self):
        """Center the dialog on screen"""
        self.geometry("+%d+%d" % (self.master.winfo_rootx() + 50, self.master.winfo_rooty() + 50))
        
    def create_widgets(self):
        """Create dialog widgets with adaptive layout"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text="🔐 Подписка и оплата",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=(0, 20))
        
        # Content area with scroll
        content_frame = ctk.CTkScrollableFrame(main_frame, height=400)
        content_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Status frame
        status_frame = ctk.CTkFrame(content_frame)
        status_frame.pack(fill="x", pady=(0, 15))
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="📊 Текущий статус",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.create_status_widgets(status_frame)
        
        # Plans frame
        if self.available_plans:
            plans_frame = ctk.CTkFrame(content_frame)
            plans_frame.pack(fill="x", pady=(0, 15))
            
            plans_label = ctk.CTkLabel(
                plans_frame,
                text="📋 Доступные планы подписки",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            plans_label.pack(anchor="w", padx=15, pady=(15, 5))
            
            self.create_plans_widgets(plans_frame)
        
        # Credits frame
        if self.credit_packages:
            credits_frame = ctk.CTkFrame(content_frame)
            credits_frame.pack(fill="x", pady=(0, 15))
            
            credits_label = ctk.CTkLabel(
                credits_frame,
                text="💰 Пакеты кредитов",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            credits_label.pack(anchor="w", padx=15, pady=(15, 5))
            
            self.create_credits_widgets(credits_frame)
        
        # Fixed buttons frame at bottom
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Purchase button
        if self.purchase_url:
            purchase_btn = ctk.CTkButton(
                buttons_frame,
                text="💳 Перейти к оплате",
                command=self.open_purchase_url,
                font=ctk.CTkFont(size=14, weight="bold"),
                height=40,
                width=150
            )
            purchase_btn.pack(side="left", padx=(0, 10), pady=10)
        
        # Close button
        close_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Закрыть",
            command=self.cancel,
            font=ctk.CTkFont(size=14),
            height=40,
            width=120,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        close_btn.pack(side="right", pady=10)
        
    def create_status_widgets(self, parent):
        """Create status information widgets"""
        status_text = ctk.CTkTextbox(parent, height=100, wrap="word")
        status_text.pack(fill="x", padx=15, pady=(0, 15))
        
        # Build status text
        status_info = []
        if self.subscription_status:
            is_active = self.subscription_status.get("is_active", False)
            days_remaining = self.subscription_status.get("days_remaining", 0)
            requests_remaining = self.subscription_status.get("requests_remaining", 0)
            plan = self.subscription_status.get("plan", "none")
            
            if is_active:
                status_info.append(f"✅ Подписка активна (план: {plan})")
                if days_remaining > 0:
                    status_info.append(f"📅 Осталось дней: {days_remaining}")
                if requests_remaining > 0:
                    status_info.append(f"💬 Осталось запросов: {requests_remaining}")
            else:
                status_info.append("❌ Подписка неактивна")
                if days_remaining < 0:
                    status_info.append(f"⚠️ Подписка просрочена на {abs(days_remaining)} дней")
                elif plan != "none":
                    status_info.append(f"📋 План: {plan} (неактивен)")
        else:
            status_info.append("❌ Подписка отсутствует")
        
        status_text.insert("1.0", "\n".join(status_info))
        status_text.configure(state="disabled")
    
    def create_plans_widgets(self, parent):
        """Create subscription plans widgets"""
        for plan in self.available_plans:
            plan_frame = ctk.CTkFrame(parent)
            plan_frame.pack(fill="x", padx=15, pady=5)
            
            plan_name = ctk.CTkLabel(
                plan_frame,
                text=f"📦 {plan.get('name', 'Безымянный план')}",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            plan_name.pack(anchor="w", padx=10, pady=(5, 2))
            
            plan_price = ctk.CTkLabel(
                plan_frame,
                text=f"💰 Цена: {plan.get('price', 'Не указана')}",
                font=ctk.CTkFont(size=11)
            )
            plan_price.pack(anchor="w", padx=10, pady=(0, 5))
            
            if plan.get('description'):
                plan_desc = ctk.CTkLabel(
                    plan_frame,
                    text=f"📝 {plan.get('description')}",
                    font=ctk.CTkFont(size=10),
                    text_color="#6c757d"
                )
                plan_desc.pack(anchor="w", padx=10, pady=(0, 5))
    
    def create_credits_widgets(self, parent):
        """Create credit packages widgets"""
        for package in self.credit_packages:
            package_frame = ctk.CTkFrame(parent)
            package_frame.pack(fill="x", padx=15, pady=5)
            
            package_name = ctk.CTkLabel(
                package_frame,
                text=f"💳 {package.get('name', 'Безымянный пакет')}",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            package_name.pack(anchor="w", padx=10, pady=(5, 2))
            
            package_price = ctk.CTkLabel(
                package_frame,
                text=f"💰 Цена: {package.get('price', 'Не указана')}",
                font=ctk.CTkFont(size=11)
            )
            package_price.pack(anchor="w", padx=10, pady=(0, 5))
            
            if package.get('credits'):
                package_credits = ctk.CTkLabel(
                    package_frame,
                    text=f"🎯 Кредиты: {package.get('credits')}",
                    font=ctk.CTkFont(size=11)
                )
                package_credits.pack(anchor="w", padx=10, pady=(0, 5))
    
    def open_purchase_url(self):
        """Open purchase URL in browser"""
        try:
            if self.purchase_url:
                webbrowser.open(self.purchase_url)
                self.logger.info(f"Opened purchase URL: {self.purchase_url}")
            else:
                messagebox.showwarning("Предупреждение", "URL для покупки не указан")
        except Exception as e:
            self.logger.error(f"Error opening purchase URL: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть URL: {str(e)}")
    
    def cancel(self):
        """Cancel dialog"""
        self.result = False
        self.destroy()