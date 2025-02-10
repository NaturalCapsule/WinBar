def layout1(main_layout, sys_info_layout, trash_layout, dock_layout, time_layout, wifi_layout, battery_layout, menu_layout, show_battery):
    main_layout.addLayout(sys_info_layout)
    main_layout.addLayout(trash_layout)
    main_layout.addLayout(menu_layout)
    main_layout.addStretch()
    main_layout.addLayout(dock_layout)
    main_layout.addStretch()
    main_layout.addLayout(wifi_layout)
    if show_battery:
        main_layout.addLayout(battery_layout)
    main_layout.addLayout(time_layout)

def layout2(main_layout, sys_info_layout, trash_layout, dock_layout, time_layout, wifi_layout, battery_layout, menu_layout, show_battery):
    main_layout.addLayout(sys_info_layout)
    main_layout.addLayout(menu_layout)
    main_layout.addStretch()
    main_layout.addLayout(dock_layout)
    main_layout.addStretch()
    main_layout.addLayout(trash_layout)
    main_layout.addLayout(wifi_layout)
    if show_battery:
        main_layout.addLayout(battery_layout)
    main_layout.addLayout(time_layout)

def layout3(main_layout, sys_info_layout, dock_layout, time_layout, wifi_layout, battery_layout, menu_layout, show_battery):
    main_layout.addLayout(sys_info_layout)
    main_layout.addLayout(menu_layout)
    main_layout.addStretch()
    main_layout.addLayout(dock_layout)
    main_layout.addStretch()
    main_layout.addLayout(wifi_layout)
    if show_battery:
        main_layout.addLayout(battery_layout)
    main_layout.addLayout(time_layout)
