import csv
import re
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from os import path
from jinja2 import Environment, FileSystemLoader
import pdfkit

experienceToRus = {
    "noExperience": "Нет опыта",
    "between1And3": "От 1 года до 3 лет",
    "between3And6": "От 3 до 6 лет",
    "moreThan6": "Более 6 лет"
}

experienceToPoints = {
    "noExperience": 0,
    "between1And3": 1,
    "between3And6": 2,
    "moreThan6": 3
}

grossToRus = {
    "true": "Без вычета налогов",
    "false": "С вычетом налогов",
    "True": "Без вычета налогов",
    "False": "С вычетом налогов",
}

currencyToRus = {
    "AZN": "Манаты",
    "BYR": "Белорусские рубли",
    "EUR": "Евро",
    "GEL": "Грузинский лари",
    "KGS": "Киргизский сом",
    "KZT": "Тенге",
    "RUR": "Рубли",
    "UAH": "Гривны",
    "USD": "Доллары",
    "UZS": "Узбекский сум"
}

currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055
}

fieldToRus = {
    "name": "Название",
    "description": "Описание",
    "key_skills": "Навыки",
    "experience_id": "Опыт работы",
    "premium": "Премиум-вакансия",
    "employer_name": "Компания",
    "salary": "Оклад",
    "salary_gross": "Оклад указан до вычета налогов",
    "salary_currency": "Идентификатор валюты оклада",
    "area_name": "Название региона",
    "published_at": "Дата публикации вакансии"
}


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


class Salary:
    def __init__(self, salary_from: str, salary_to: str, salary_currency: str):
        self.salary_from = int(float(salary_from))
        self.salary_to = int(float(salary_to))
        self.salary_currency = salary_currency

    def to_string(self):
        salary_string = '{0:,}'.format(self.salary_from).replace(',', ' ') + " - "
        salary_string += '{0:,}'.format(self.salary_to).replace(',', ' ') + " (" + currencyToRus[
            self.salary_currency] + ")"
        return salary_string


class Vacancy:
    def __init__(self, name: str, salary: Salary, area_name: str, published_at: str):
        self.name = name
        self.salary = salary
        self.area_name = area_name
        self.published_at = published_at

    def date_to_string(self):
        splitted_date = self.published_at.split("T")[0].split("-")
        date_string = splitted_date[2] + "." + splitted_date[1] + "." + splitted_date[0]
        return date_string

    def date_get_year(self):
        return int(self.date_to_string().split(".")[-1])

    def to_list(self):
        return [TextEditor.beautifulStr(self.name), self.salary.to_string(), self.area_name, self.date_to_string()]


class DataSet:
    def __init__(self, ﬁle_name: str, vacancies_objects: list):
        self.file_name = file_name
        self.vacancies_objects = vacancies_objects


class TextEditor:
    def beautifulStr(string: str):
        return ' '.join(re.sub(r"<[^>]+>", '', string).split()).replace("  ", " ").replace(" ", " ")

    def line_trim(string: str):
        if len(string) > 100:
            string = string[:100] + "..."
        return string

    def formatter(field: str, string: str):
        if (field == "premium"):
            string = string.replace("FALSE", "Нет").replace("TRUE", "Да").replace("False", "Нет").replace("True", "Да")
        elif (field == "salary_gross"):
            string = grossToRus[string.lower()]
        elif (field == "salary_currency"):
            string = currencyToRus[string]
        elif (field == "experience_id"):
            string = experienceToRus[string]
        return [fieldToRus[field], string]


class CsvWorker:
    def __init__(self, file_name: str):
        self.file_name = file_name

    def check_file(self):
        if os.stat(file_name).st_size == 0:
            print("Пустой файл")
            return False
        return True

    def csv_ﬁler(self, vacancy_in, fields):
        salary = Salary(vacancy_in[fields.index("salary_from")], vacancy_in[fields.index("salary_to")],
                        vacancy_in[fields.index("salary_currency")])
        vacancy = Vacancy(vacancy_in[fields.index("name")], salary, vacancy_in[fields.index("area_name")],
                          vacancy_in[fields.index("published_at")])
        return vacancy

    def сsv_reader(self):
        fields = []
        vacancies = []
        with open(ﬁle_name, encoding="UTF-8-sig") as File:
            reader = csv.reader(File, delimiter=',')
            for row in reader:
                if (fields == []):
                    fields = row
                elif (len(fields) == len(row) and not ("" in row)):
                    vacancies.append(self.csv_ﬁler(row, fields))
        return vacancies, fields


class HtmlGenerator:
    def generate_table(self, titles, content):
        table = "<table>"
        table += self.generate_titles(titles)
        for row in content:
            table += self.generate_row(row)
        table += "</table>"
        return table

    def generate_titles(self, titles):
        string = "<tr>"
        for title in titles:
            string += "<th>" + title + "</th>"
        string += "</tr>"
        return string

    def generate_row(self, row):
        string = "<tr>"
        for row_item in row:
            string += "<td>" + str(row_item) + "</td>"
        string += "</tr>"
        return string

    def generate_html(self, dicts, image_path, prof_name):
        html = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Report</title>
                    </head>
                    <style>
                    body{
                        font-family: Verdana;
                    }
                    table{
                        text-align: center;
                        border-collapse: collapse;
                    }
                    th, td{
                        border: 1px solid;
                        padding: 5px;
                    }
                    </style>
                    <body>
                    <h1 style="text-align: center; font-size: 60px;">Аналитика по зарплатам и городам для профессии """ + prof_name + """</h1>
                    <img src=\"""" + image_path + """\">"""
        # 1
        titles = ["Год", "Средняя зарплата", "Средняя зарплата - " + prof_name, "Количество вакансий",
                  "Количество вакансий - " + prof_name]
        html += "<h1 style='text-align:center;'>Статистика по годам</h1>"
        html += "<table style='width: 100%;'>" + self.generate_titles(titles)
        dict = dicts[0]
        for i in range(len(dict[0])):
            year = dict[0][i]
            avgSalary = list(dict[1].values())[i]
            avgSalaryProf = list(dict[3].values())[i]
            vacAmount = list(dict[2].values())[i]
            vacAmountProf = list(dict[4].values())[i]
            row = [year, avgSalary, avgSalaryProf, vacAmount, vacAmountProf]
            html += self.generate_row(row)
        html += """</table> <br>"""

        # 2
        titles = ["Город", "Уровень зарплат"]
        html += "<h1 style='text-align:center;'>Статистика по городам</h1>"
        html += "<table style='float: left; width: 45%;'>" + self.generate_titles(titles)
        dict = dicts[1][0]
        values = list(dict.values())
        keys = list(dict.keys())
        for i in range(len(values)):
            city = keys[i]
            avgSalary = values[i]
            row = [city, avgSalary]
            html += self.generate_row(row)
        html += "</table>"

        # 3
        titles = ["Город", "Доля вакансий"]
        html += "<table style='float: right; width: 45%;'>" + self.generate_titles(titles)
        dict = dicts[1][1]
        values = list(dict.values())
        keys = list(dict.keys())
        for i in range(len(values)):
            city = keys[i]
            percent = str(values[i] * 100).replace(".", ",") + "%"
            row = [city, percent]
            html += self.generate_row(row)
        html += "</table></body></html>"
        return html


class Report:
    def __init__(self, name, dicts, prof_name):
        generator = HtmlGenerator()
        parent_dir = path.dirname(path.abspath(__file__))
        self.filename = name
        self.generate_graph(dicts, prof_name)
        self.html = generator.generate_html(dicts, parent_dir + '/temp.png', prof_name)

    def generate_graph(self, dicts, prof_name):
        dictsSalary = dicts[0]
        dictsCities = dicts[1]
        years = dictsSalary[0]
        plt.grid(axis='y')
        plt.style.use('ggplot')
        plt.rcParams.update({'font.size': 8})

        x = np.arange(len(years))
        width = 0.35
        ax = plt.subplot(2, 2, 1)
        ax.bar(x - width / 2, dictsSalary[1].values(), width, label='средняя з/п')
        ax.bar(x + width / 2, dictsSalary[3].values(), width, label='з/п ' + prof_name)
        ax.legend()
        ax.set_xticks(x, years, rotation=90)
        plt.title("Уровень зарплат по годам")

        ax = plt.subplot(2, 2, 2)
        ax.bar(x - width / 2, dictsSalary[2].values(), width, label='Количество вакансий')
        ax.bar(x + width / 2, dictsSalary[4].values(), width, label='Количество вакансий\n' + prof_name)
        ax.legend()
        ax.set_xticks(x, years, rotation=90)
        plt.title("Количество вакансий по годам")

        plt.subplot(2, 2, 3)
        plt.barh(list(reversed(list(dictsCities[0].keys()))), list(reversed(dictsCities[0].values())), alpha=0.8, )
        plt.title("Уровень зарплат по городам")

        plt.subplot(2, 2, 4)
        plt.pie(list(dictsCities[1].values()) + [1 - sum(list(dictsCities[1].values()))],
                labels=list(dictsCities[1].keys()) + ["Другие"])
        plt.title("Доля вакансий по городам")
        plt.subplots_adjust(wspace=0.5, hspace=0.5)

        plt.savefig("temp.png", dpi=200, bbox_inches='tight')


def get_data(vacancies_objects, prof_name):
    dict = {"salary": {},
            "amount": {},
            "salary_prof": {},
            "amount_prof": {},
            "salary_city": {},
            "amount_city": {}}
    for vacancy in vacancies_objects:
        avg_salary = (vacancy.salary.salary_from + vacancy.salary.salary_to) / 2 * currency_to_rub[
            vacancy.salary.salary_currency]
        year = vacancy.date_get_year()
        # Динамика уровня зарплат по годам
        if year not in dict["salary"]:
            dict["salary"][year] = [avg_salary]
        else:
            dict["salary"][year] += [avg_salary]
        # Динамика количества вакансий по годам
        if year not in dict["amount"]:
            dict["amount"][year] = 1
        else:
            dict["amount"][year] += 1
        if prof_name in vacancy.name:
            # Динамика уровня зарплат по годам для выбранной профессии
            if year not in dict["salary_prof"].keys():
                dict["salary_prof"][year] = [avg_salary]
            else:
                dict["salary_prof"][year] += [avg_salary]
            # Динамика количества вакансий по годам для выбранной профессии
            if year not in dict["amount_prof"].keys():
                dict["amount_prof"][year] = 1
            else:
                dict["amount_prof"][year] += 1

        # Уровень зарплат по городам (в порядке убывания)
        if vacancy.area_name not in dict["salary_city"]:
            dict["salary_city"][vacancy.area_name] = [avg_salary]
        else:
            dict["salary_city"][vacancy.area_name] += [avg_salary]
        # Доля вакансий по городам (в порядке убывания)
        if vacancy.area_name not in dict["amount_city"]:
            dict["amount_city"][vacancy.area_name] = 1
        else:
            dict["amount_city"][vacancy.area_name] += 1
    return dict


def print_data(data, total_vacancies):
    temp = {}
    salaryDict = []
    cityDict = []
    for x in data["salary"].keys():
        temp[x] = int(sum(data["salary"][x]) / len(data["salary"][x]))
    print("Динамика уровня зарплат по годам:", temp)
    salaryDict.append(list(list(data["salary"].keys())[i] for i in range(len(data["salary"].keys()))))
    salaryDict.append(temp)
    print("Динамика количества вакансий по годам:", data["amount"])
    salaryDict.append(data["amount"])
    temp = {list(data["salary"].keys())[i]: 0 for i in range(len(data["salary"].keys()))}
    for x in data["salary_prof"].keys():
        temp[x] = int(sum(data["salary_prof"][x]) / len(data["salary_prof"][x]))
    print("Динамика уровня зарплат по годам для выбранной профессии:", temp)
    salaryDict.append(temp)

    if len(data["amount_prof"]) != 0:
        print("Динамика количества вакансий по годам для выбранной профессии:", data["amount_prof"])
        salaryDict.append(data["amount_prof"])
    else:
        temp = {list(data["salary"].keys())[i]: 0 for i in range(len(data["salary"].keys()))}
        print("Динамика количества вакансий по годам для выбранной профессии:", temp)

        salaryDict.append(temp)

    temp = {}
    if "Россия" in data["salary_city"]:
        data["salary_city"].pop("Россия")
    for x in data["salary_city"].keys():
        percent = len(data["salary_city"][x]) / total_vacancies
        if (percent >= 0.01):
            temp[x] = int(sum(data["salary_city"][x]) / len(data["salary_city"][x]))
    temp = dict(sorted(temp.items(), key=lambda x: x[1], reverse=True)[:10])
    print("Уровень зарплат по городам (в порядке убывания):", temp)
    cityDict.append(temp)
    temp = {}
    if "Россия" in data["amount_city"]:
        data["amount_city"].pop("Россия")
    for x in data["amount_city"].keys():
        percent = data["amount_city"][x] / total_vacancies
        if (percent >= 0.01):
            temp[x] = round(percent, 4)
    temp = dict(sorted(temp.items(), key=lambda x: x[1], reverse=True)[:10])
    print("Доля вакансий по городам (в порядке убывания):", temp)
    cityDict.append(temp)
    return [salaryDict, cityDict]


options = {'enable-local-file-access': None}
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

file_name = input("Введите название файла: ")
prof_name = input("Введите название профессии: ")

csv_worker = CsvWorker(file_name)
vacancies_objects, _ = csv_worker.сsv_reader()
data_set = DataSet(file_name, vacancies_objects)
data = get_data(vacancies_objects, prof_name)

generator = HtmlGenerator()

report = Report("graph.jpg", print_data(data, len(vacancies_objects)), prof_name)
pdfkit.from_string(report.html, 'report.pdf', configuration=config, options=options)