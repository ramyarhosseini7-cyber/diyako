import flet as ft
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

DB_FILE = "documents.json"

def load_documents():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_documents_to_db(docs):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=4)

def generate_pdf(title, content):
    file_name = f"{title.replace(' ', '_')}.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, title)
    c.setFont("Helvetica", 12)
    text_object = c.beginText(100, 720)
    for line in content.split("\n"):
        text_object.textLine(line)
    c.drawText(text_object)
    c.save()
    return file_name

def main(page: ft.Page):
    page.title = "DIYAKO"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 380
    page.window_height = 700
    page.scroll = ft.ScrollMode.AUTO

    documents = load_documents()

    def toggle_theme(e=None):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        page.update()

    def go_to_dashboard(e=None):
        page.clean()
        page.add(build_dashboard_view())

    def open_new_document(doc_data=None):
        page.clean()
        page.add(build_editor_view(doc_data))

    def open_my_documents(e=None):
        page.clean()
        page.add(build_my_documents_view())

    def open_pdf_tools(e=None):
        page.clean()
        page.add(build_pdf_tools_view())

    def open_settings(e=None):
        page.clean()
        page.add(build_settings_view())

    def open_dedication(e=None):
        page.clean()
        page.add(build_dedication_view())

    # ------------------ ۱. داشبورد ------------------
    def build_dashboard_view():
        header = ft.Row([
            ft.Text("DIYAKO", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.IconButton(icon=ft.Icons.BRIGHTNESS_4, on_click=toggle_theme)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        def build_card(title, sub, icon, color, on_click=None):
            return ft.Container(
                content=ft.Row([
                    ft.Icon(icon, size=28, color=color),
                    ft.Column([
                        ft.Text(title, size=15, weight=ft.FontWeight.BOLD),
                        ft.Text(sub, size=11, color=ft.Colors.GREY_400)
                    ], spacing=2)
                ], spacing=15),
                padding=14,
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                ink=True,
                on_click=on_click
            )

        menu = ft.Column([
            build_card("New Document ➕", "ساخت و ویرایش سند جدید", ft.Icons.NOTE_ADD, ft.Colors.BLUE_300, on_click=lambda e: open_new_document()),
            build_card("My Documents 📂", "مدیریت و مشاهده اسناد ذخیره‌شده", ft.Icons.FOLDER, ft.Colors.AMBER_300, on_click=open_my_documents),
            build_card("PDF Tools 📄", "تبدیل عکس به PDF و ابزارها", ft.Icons.PICTURE_IN_PICTURE, ft.Colors.GREEN_300, on_click=open_pdf_tools),
            build_card("Settings ⚙️", "تنظیمات برنامه و ظاهری", ft.Icons.SETTINGS, ft.Colors.PURPLE_300, on_click=open_settings),
            build_card("تقدیم به برادرم پویا 🎖️", "پیام ویژه سازنده برنامه (رامیار)", ft.Icons.MILITARY_TECH, ft.Colors.RED_400, on_click=open_dedication),
        ], spacing=12)

        recent_list = ft.Column(spacing=8)
        if not documents:
            recent_list.controls.append(ft.Container(content=ft.Text("هنوز سندی ایجاد نشده است.", color=ft.Colors.GREY_500, size=13), padding=20, alignment=ft.Alignment(0, 0)))
        else:
            for doc in reversed(documents[-5:]):
                recent_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DESCRIPTION, color=ft.Colors.BLUE_200, size=20),
                            ft.Text(doc["title"], size=14, weight=ft.FontWeight.W_500)
                        ], spacing=10),
                        padding=10, border_radius=8, bgcolor=ft.Colors.SURFACE_CONTAINER,
                        on_click=lambda e, d=doc: open_new_document(d)
                    )
                )

        return ft.Column([header, ft.Divider(height=10, color=ft.Colors.TRANSPARENT), menu, ft.Divider(height=20), ft.Text("اسناد اخیر", size=16, weight=ft.FontWeight.BOLD), recent_list])

    # ------------------ ۲. اسناد من ------------------
    def build_my_documents_view():
        header = ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_to_dashboard),
            ft.Text("اسناد من", size=20, weight=ft.FontWeight.BOLD),
            ft.IconButton(icon=ft.Icons.BRIGHTNESS_4, on_click=toggle_theme)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        doc_list_column = ft.Column(spacing=10)
        def delete_doc(doc_to_delete):
            documents.remove(doc_to_delete)
            save_documents_to_db(documents)
            page.clean()
            page.add(build_my_documents_view())

        if not documents:
            doc_list_column.controls.append(ft.Container(content=ft.Text("هیچ سندی ذخیره نشده است.", color=ft.Colors.GREY_500, size=13), padding=30, alignment=ft.Alignment(0, 0)))
        else:
            for doc in reversed(documents):
                doc_list_column.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Row([ft.Icon(ft.Icons.ARTICLE, color=ft.Colors.AMBER_400, size=24), ft.Text(doc["title"], size=15, weight=ft.FontWeight.W_500)], spacing=10),
                            ft.Row([
                                ft.IconButton(icon=ft.Icons.EDIT, icon_color=ft.Colors.BLUE_300, on_click=lambda e, d=doc: open_new_document(d)),
                                ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, on_click=lambda e, d=doc: delete_doc(d))
                            ], spacing=0)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10, border_radius=10, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
                    )
                )

        return ft.Column([header, ft.Divider(height=10, color=ft.Colors.TRANSPARENT), doc_list_column], spacing=15)

    # ------------------ ۳. ویرایشگر ------------------
    def build_editor_view(doc_data=None):
        initial_title = doc_data["title"] if doc_data else ""
        initial_content = doc_data["content"] if doc_data else ""

        doc_title_input = ft.TextField(label="عنوان سند", value=initial_title, hint_text="مثلاً: Test Document", border_radius=10)
        doc_content_input = ft.TextField(label="متن سند", value=initial_content, hint_text="شروع به نوشتن کنید...", multiline=True, min_lines=12, max_lines=18, border_radius=10)
        status_text = ft.Text("", color=ft.Colors.GREEN_400, size=13)

        def save_document(e):
            if not doc_title_input.value:
                status_text.value = "لطفاً ابتدا یک عنوان وارد کنید."
                status_text.color = ft.Colors.RED_400
            else:
                if doc_data in documents:
                    doc_data["title"] = doc_title_input.value
                    doc_data["content"] = doc_content_input.value
                else:
                    documents.append({"title": doc_title_input.value, "content": doc_content_input.value})
                save_documents_to_db(documents)
                status_text.value = f"سند '{doc_title_input.value}' ذخیره شد!"
                status_text.color = ft.Colors.GREEN_400
            page.update()

        def export_pdf(e):
            if not doc_title_input.value:
                status_text.value = "عنوان را وارد کنید."
                status_text.color = ft.Colors.RED_400
            else:
                try:
                    pdf_path = generate_pdf(doc_title_input.value, doc_content_input.value)
                    status_text.value = f"فایل PDF '{pdf_path}' ساخته شد! 📄"
                    status_text.color = ft.Colors.GREEN_400
                except Exception as err:
                    status_text.value = f"خطا: {err}"
                    status_text.color = ft.Colors.RED_400
            page.update()

        header = ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_to_dashboard),
            ft.Text("ویرایشگر سند", size=20, weight=ft.FontWeight.BOLD),
            ft.IconButton(icon=ft.Icons.BRIGHTNESS_4, on_click=toggle_theme)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        actions = ft.Row([
            ft.ElevatedButton("ذخیره سند 💾", on_click=save_document, style=ft.ButtonStyle(color=ft.Colors.BLUE_400)),
            ft.OutlinedButton("خروجی PDF 📄", on_click=export_pdf)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        return ft.Column([header, ft.Divider(height=10, color=ft.Colors.TRANSPARENT), doc_title_input, doc_content_input, actions, status_text], spacing=15)

    # ------------------ ۴. ابزارهای PDF ------------------
    def build_pdf_tools_view():
        header = ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_to_dashboard),
            ft.Text("ابزارهای PDF", size=20, weight=ft.FontWeight.BOLD),
            ft.IconButton(icon=ft.Icons.BRIGHTNESS_4, on_click=toggle_theme)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        img_path_input = ft.TextField(label="آدرس تصویر (Image Path)", hint_text="مثلاً sample.jpg", border_radius=10)
        status_text = ft.Text("", color=ft.Colors.GREEN_400, size=13)

        def convert_img_to_pdf(e):
            if not img_path_input.value:
                status_text.value = "آدرس تصویر را وارد کنید."
                status_text.color = ft.Colors.RED_400
            else:
                try:
                    path = img_path_input.value
                    image = Image.open(path)
                    pdf_path = path.rsplit(".", 1)[0] + ".pdf"
                    image.convert("RGB").save(pdf_path)
                    status_text.value = f"تصویر به '{pdf_path}' تبدیل شد! 📄"
                    status_text.color = ft.Colors.GREEN_400
                except Exception:
                    status_text.value = "خطا: فایل یافت نشد."
                    status_text.color = ft.Colors.RED_400
            page.update()

        card = ft.Container(
            content=ft.Column([
                ft.Text("تبدیل تصویر به PDF 🖼️➡️📄", size=16, weight=ft.FontWeight.BOLD),
                img_path_input,
                ft.ElevatedButton("تبدیل به PDF", on_click=convert_img_to_pdf, style=ft.ButtonStyle(color=ft.Colors.GREEN_400)),
                status_text
            ], spacing=10),
            padding=15, border_radius=12, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
        )

        return ft.Column([header, ft.Divider(height=10, color=ft.Colors.TRANSPARENT), card], spacing=15)

    # ------------------ ۵. تنظیمات (Settings) ------------------
    def build_settings_view():
        header = ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_to_dashboard),
            ft.Text("تنظیمات", size=20, weight=ft.FontWeight.BOLD),
            ft.IconButton(icon=ft.Icons.BRIGHTNESS_4, on_click=toggle_theme)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        status_text = ft.Text("", color=ft.Colors.RED_400, size=13)

        def clear_all_data(e):
            nonlocal documents
            documents = []
            save_documents_to_db(documents)
            status_text.value = "تمام اطلاعات و اسناد با موفقیت پاک شدند!"
            status_text.color = ft.Colors.GREEN_400
            page.update()

        settings_list = ft.Column([
            ft.ListTile(
                leading=ft.Icon(ft.Icons.MILITARY_TECH, color=ft.Colors.RED_400),
                title=ft.Text("تقدیم به برادرم پویا 🎖️"),
                on_click=open_dedication
            ),
            ft.Divider(height=1),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PALETTE, color=ft.Colors.PURPLE_300),
                title=ft.Text("تغییر تم (Dark / Light)"),
                on_click=toggle_theme
            ),
            ft.Divider(height=1),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DELETE_FOREVER, color=ft.Colors.RED_400),
                title=ft.Text("حذف تمام اسناد و داده‌ها"),
                on_click=clear_all_data
            ),
            ft.Divider(height=1),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.INFO_OUTLINED, color=ft.Colors.BLUE_300),
                title=ft.Text("درباره برنامه"),
                subtitle=ft.Text("DIYAKO App v1.0.0\nDeveloper: Ramyar Hosseini")
            )
        ], spacing=5)

        return ft.Column([
            header,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Container(content=settings_list, padding=10, border_radius=12, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
            status_text
        ], spacing=15)

    # ------------------ ۶. صفحه اختصاصی تقدیم به پویا ------------------
    def build_dedication_view():
        header = ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_to_dashboard),
            ft.Text("تقدیم‌نامه", size=20, weight=ft.FontWeight.BOLD),
            ft.IconButton(icon=ft.Icons.BRIGHTNESS_4, on_click=toggle_theme)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        card_content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SECURITY, size=36, color=ft.Colors.BLUE_400),
                ft.Icon(ft.Icons.FAVORITE, size=36, color=ft.Colors.RED_400),
                ft.Icon(ft.Icons.MILITARY_TECH, size=36, color=ft.Colors.AMBER_400)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Text("تقدیم به برادر عزیزم، پویا 🎖️", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "این برنامه با عشق و افتخار توسط برادر کوچکت، رامیار حسینی، ساخته شده است.\n\n"
                "تقدیم به پویا جان که این روزها در پادگان و در سنگر حفظ امنیت کشور، مایه غرور و افتخار همه ماست.\n\n"
                "به امید سلامتی، سربلندی و موفقیت روزافزون تو برادر شجاعم. ❤️",
                size=14,
                color=ft.Colors.GREY_200,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Divider(height=15),
            ft.Text("طراح و توسعه‌دهنده: رامیار حسینی", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)

        dedicated_card = ft.Container(
            content=card_content,
            padding=20,
            border_radius=15,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border=ft.Border.all(1, ft.Colors.BLUE_400)
        )

        return ft.Column([header, ft.Divider(height=15, color=ft.Colors.TRANSPARENT), dedicated_card], spacing=15)

    page.add(build_dashboard_view())

ft.app(target=main, view=ft.AppView.FLET_APP)