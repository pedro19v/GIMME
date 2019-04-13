#pragma once

#include <QtWidgets/QMainWindow>
#include "ui_GIMMEUI.h"

//include core functionalities
#include "../GIMMECore/headers/GIMMECore.h"

class GIMMEUI : public QMainWindow
{
	Q_OBJECT

public:
	GIMMEUI(QWidget *parent = Q_NULLPTR);

private:
	Ui::GIMMEUIClass ui;
};
