/********************************************************************************
** Form generated from reading UI file 'GIMMEToolUI.ui'
**
** Created by: Qt User Interface Compiler version 5.12.2
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_GIMMETOOLUI_H
#define UI_GIMMETOOLUI_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QToolBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_GIMMEToolUIClass
{
public:
    QMenuBar *menuBar;
    QToolBar *mainToolBar;
    QWidget *centralWidget;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *GIMMEToolUIClass)
    {
        if (GIMMEToolUIClass->objectName().isEmpty())
            GIMMEToolUIClass->setObjectName(QString::fromUtf8("GIMMEToolUIClass"));
        GIMMEToolUIClass->resize(600, 400);
        menuBar = new QMenuBar(GIMMEToolUIClass);
        menuBar->setObjectName(QString::fromUtf8("menuBar"));
        GIMMEToolUIClass->setMenuBar(menuBar);
        mainToolBar = new QToolBar(GIMMEToolUIClass);
        mainToolBar->setObjectName(QString::fromUtf8("mainToolBar"));
        GIMMEToolUIClass->addToolBar(mainToolBar);
        centralWidget = new QWidget(GIMMEToolUIClass);
        centralWidget->setObjectName(QString::fromUtf8("centralWidget"));
        GIMMEToolUIClass->setCentralWidget(centralWidget);
        statusBar = new QStatusBar(GIMMEToolUIClass);
        statusBar->setObjectName(QString::fromUtf8("statusBar"));
        GIMMEToolUIClass->setStatusBar(statusBar);

        retranslateUi(GIMMEToolUIClass);

        QMetaObject::connectSlotsByName(GIMMEToolUIClass);
    } // setupUi

    void retranslateUi(QMainWindow *GIMMEToolUIClass)
    {
        GIMMEToolUIClass->setWindowTitle(QApplication::translate("GIMMEToolUIClass", "GIMMEToolUI", nullptr));
    } // retranslateUi

};

namespace Ui {
    class GIMMEToolUIClass: public Ui_GIMMEToolUIClass {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_GIMMETOOLUI_H
