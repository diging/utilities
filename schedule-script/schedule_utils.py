from datetime import time, datetime, date, timedelta
from openpyxl.styles import Font, Color, PatternFill, Alignment, Border, Side

def handle_lunch(duration, cell_string, total_scheduled_hours):
    if (duration.seconds / 60) > 300:
        print('duration_2: {}'.format(duration.seconds))
        cell_string = cell_string + ' (1/2 hour lunch)'
        total_scheduled_hours -= timedelta(minutes=30)
    return total_scheduled_hours, cell_string

def format_cell(new_sheet, row_number, start_column, end_column, background_colors, rectangle_border):
    schedule_cell = new_sheet.cell(row=row_number, column=start_column)
    schedule_cell.fill = PatternFill("solid", fgColor=background_colors)
    schedule_cell.border = rectangle_border
    new_sheet.merge_cells(start_row=row_number, start_column=start_column, end_row=row_number, end_column=end_column)
    return schedule_cell