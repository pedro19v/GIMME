#pragma once

#include <QtWidgets/QMainWindow>
#include "ui_GIMMEToolUI.h"

class GIMMEToolUI : public QMainWindow
{
	Q_OBJECT

public:
	GIMMEToolUI(QWidget *parent = Q_NULLPTR);

private:
	Ui::GIMMEToolUIClass ui;
};
