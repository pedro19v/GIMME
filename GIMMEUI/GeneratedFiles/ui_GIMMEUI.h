/********************************************************************************
** Form generated from reading UI file 'GIMMEUI.ui'
**
** Created by: Qt User Interface Compiler version 5.12.2
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_GIMMEUI_H
#define UI_GIMMEUI_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QToolBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_GIMMEUIClass
{
public:
    QMenuBar *menuBar;
    QToolBar *mainToolBar;
    QWidget *centralWidget;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *GIMMEUIClass)
    {
        if (GIMMEUIClass->objectName().isEmpty())
            GIMMEUIClass->setObjectName(QString::fromUtf8("GIMMEUIClass"));
        GIMMEUIClass->resize(600, 400);
        menuBar = new QMenuBar(GIMMEUIClass);
        menuBar->setObjectName(QString::fromUtf8("menuBar"));
        GIMMEUIClass->setMenuBar(menuBar);
        mainToolBar = new QToolBar(GIMMEUIClass);
        mainToolBar->setObjectName(QString::fromUtf8("mainToolBar"));
        GIMMEUIClass->addToolBar(mainToolBar);
        centralWidget = new QWidget(GIMMEUIClass);
        centralWidget->setObjectName(QString::fromUtf8("centralWidget"));
        GIMMEUIClass->setCentralWidget(centralWidget);
        statusBar = new QStatusBar(GIMMEUIClass);
        statusBar->setObjectName(QString::fromUtf8("statusBar"));
        GIMMEUIClass->setStatusBar(statusBar);

        retranslateUi(GIMMEUIClass);

        QMetaObject::connectSlotsByName(GIMMEUIClass);
    } // setupUi

    void retranslateUi(QMainWindow *GIMMEUIClass)
    {
        GIMMEUIClass->setWindowTitle(QApplication::translate("GIMMEUIClass", "GIMMEUI", nullptr));
    } // retranslateUi

};

namespace Ui {
    class GIMMEUIClass: public Ui_GIMMEUIClass {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_GIMMEUI_H
