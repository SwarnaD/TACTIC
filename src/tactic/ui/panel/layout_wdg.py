###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

from __future__ import print_function


__all__ = ["AddPredefinedColumnWdg", "SwitchLayoutMenu", "CellEditWdg", "CellWdg", "EditColumnDefinitionWdg", "EditColumnDefinitionCbk"]


import types
import re
from pyasm.common import Environment, TacticException, Common, Container, Xml, Date, UserException, Config, jsonloads, jsondumps
from pyasm.command import Command
from pyasm.search import Search, SearchKey, SObject, SearchType, WidgetDbConfig, Sql, SqlException
from pyasm.web import *
from pyasm.biz import *   # Project is part of pyasm.biz

from pyasm.widget import TextWdg, TextAreaWdg, SelectWdg, \
     WidgetConfigView, WidgetConfig, CheckboxWdg, SearchLimitWdg, IconWdg, \
     EditLinkWdg, FilterSelectWdg, ProdIconButtonWdg, IconButtonWdg, HiddenWdg,\
     SwapDisplayWdg, HintWdg


from pyasm.prod.biz import ProdSetting

from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg, SimpleTableElementWdg
from tactic.ui.container import PopupWdg, HorizLayoutWdg,  SmartMenu
from tactic.ui.widget import DgTableGearMenuWdg, TextBtnSetWdg, CalendarInputWdg, DynByFoundValueSmartSelectWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu

from tactic.ui.common import BaseConfigWdg


import sys, traceback, six




class SwitchLayoutMenu(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.search_type = self.kwargs.get("search_type")
        activator = self.kwargs.get("activator")
        self.view = self.kwargs.get("view")
        self.custom_views = self.kwargs.get("custom_views") or None
        default_views = self.kwargs.get("default_views")

        menu = Menu(width=180, allow_icons=True)
        menu_item = MenuItem(type='title', label='Switch Layout')
        menu.add(menu_item)

        config = WidgetConfigView.get_by_search_type(self.search_type, "table")
        default_element_names = config.get_element_names()


        views = ['table', 'tile', 'list', 'content', 'navigate', 'schedule', 'checkin', 'tool', 'browser', 'card', 'collection', 'overview']
        labels = ['Table', 'Tile', 'List', 'Content', 'Navigator', 'Task Schedule', 'Check-in', 'Tools', 'File Browser', 'Card', 'Collection', 'Overview']

        # this is fast table biased
        if self.kwargs.get("is_refresh") in ['false', False]:
            class_names = [
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
            ]
        else:
            class_names = [
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.TileLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.tool_layout_wdg.ToolLayoutWdg',
                'tactic.ui.panel.tool_layout_wdg.RepoBrowserLayoutWdg',
                'tactic.ui.panel.tool_layout_wdg.CardLayoutWdg',
                'tactic.ui.panel.collection_wdg.CollectionLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
            ]


        layouts = [
            'table',
            'tile',
            'default',
            'default',
            'default',
            'default',
            'default',
            'tool',
            'browser',
            'card',
            'collection',
            'default',
        ]

        element_names = [
            default_element_names,
            [],
            ['name'],
            ['preview','code','name','description'],
            ['show_related','detail','code','description'],
            ['preview','code','name','description','task_pipeline_vertical','task_edit','notes'],
            ['preview','code','name','general_checkin','file_list', 'history','description','notes'],
            ['name','description','detail', 'file_list','general_checkin'],
            [],
            [],
            [],
            ['preview','name','task_pipeline_report','summary','completion'],
	    ]

        if not SearchType.column_exists(self.search_type, 'name'):
            element_names = [
            default_element_names,
            [],
            ['code'],
            ['preview','code','description'],
            ['show_related','detail','code','description'],
            ['preview','code','description','task_pipeline_vertical','task_edit','notes'],
            ['preview','code','general_checkin','file_list', 'history','description','notes'],
            [],
            [],
            [],
            [],
            ['preview','code','task_pipeline_report','summary','completion'],
	    ]

        if default_views in ['false', False]:
            views = []
            labels = []
            class_names = []
            layouts = []
            element_names = []

        if self.custom_views:
            for key, val in self.custom_views.items():
                views.append(key)
                labels.append(val[0])
                class_names.append(val[1])
                layouts.append(val[2])
                element_names.append(val[3])

        # add in the default
        #views.insert(0, self.view)
        #labels.insert(0, self.view)
        #class_names.insert(0, 'tactic.ui.panel.FastTableLayoutWdg')
        #layouts.insert(0, "tile")
        #element_names.insert(0, None)

        cbk = self.kwargs.get("cbk")
        if not cbk:
            cbk = '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_view_panel_top");
            if (!top) {
                alert("Error: spt_view_panel_top not found");
                return;
            }

          
            var table_top = top.getElement(".spt_table_top");
            

            //var layout = top.getAttribute("spt_layout");
            if (table_top){
                var layout_el = top.getElement(".spt_layout");
                var version = layout_el.getAttribute("spt_version") || 1;
                if (version =='2') {
                    var table = table_top.getElement(".spt_table_table");
                } else {
                    var table = table_top.getElement(".spt_table");
                }
            } else {
                var table_top = top.getElement(".spt_calendar_top");
                var table = table_top.getElement("table");
                table.addClass("spt_table_content");
                table_top.addClass("spt_table_top");
            }

            
            top.setAttribute("spt_layout", bvr.layout);
            var last_view = top.getAttribute("spt_view");
            top.setAttribute("spt_last_view", last_view);
            top.setAttribute("spt_view", bvr.view);
            table_top.setAttribute("spt_class_name", bvr.class_name);
            table_top.setAttribute("spt_view", bvr.view);

            var ls_custom_views = top.getAttribute("spt_layout_switcher_custom_views") || "";
            if (ls_custom_views) {
                ls_custom_views = ls_custom_views.replace(/'/g, '"');
                ls_custom_views = JSON.parse(ls_custom_views);
                ls_custom_views = JSON.stringify(ls_custom_views);
                table_top.setAttribute("spt_custom_views", ls_custom_views);
            }

            if (bvr.custom_views) {
                table_top.setAttribute("spt_custom_views", bvr.custom_views);
            }
            
            table.setAttribute("spt_view", bvr.view);
            spt.dg_table.search_cbk( {}, {src_el: bvr.src_el, element_names: bvr.element_names, widths:[]} );

            '''


        from .layout_util import LayoutUtil

        for i, view in enumerate(views):
            #data = LayoutUtil.get_layout_data(search_type=self.search_type, layout=view)
            #layout = view
            #class_name = data.get("class_name")
            #element_names = data.get("element_names")
            #label = data.get("label")

            # TODO: use old method for now until we can ensure the stability
            # of the new method
            class_name = class_names[i]
            element_name_list = element_names[i]
            layout = layouts[i]
            label = labels[i]

            menu_item = MenuItem(type='action', label=label)
            if self.view == labels[i]:
                menu_item.set_icon(IconWdg.DOT_GREEN)
            menu.add(menu_item)

            menu_item.add_behavior( {
            'type': 'click_up',
            'view': view,
            'class_name': class_name,
            'element_names': element_name_list,
            'layout': layout,
            'search_type': self.search_type,
            'default_views': default_views,
            'custom_views': self.custom_views,
            'cbjs_action': cbk
            } )


        menus = [menu.get_data()]
        SmartMenu.add_smart_menu_set( activator, { 'DG_BUTTON_CTX': menus } )
        SmartMenu.assign_as_local_activator( activator, "DG_BUTTON_CTX", True )





# Cell Editing and Display
class CellEditWdg(BaseRefreshWdg):
    '''Widget which allows the editing of a cell'''

    def get_args_keys(self):
        return {
        'search_type': 'the search type of table',
        'element_name': 'element name that this widget represents',
        'x': 'the x index of the element',
        'y': 'the y index of the element',

        'state': 'specifies a set of state data for new inserts',
        'layout_version': '1 or 2'
        }



    def get_display_wdg(self):
        '''get the display widget that is contained in the cell edit'''
        return self.display_wdg


    def init(self):
        element_name = self.kwargs['element_name']
        search_type = self.kwargs['search_type']
        layout_version = self.kwargs['layout_version']

        config_xml = self.kwargs['config_xml']

        configs = Container.get("CellEditWdg:configs")
        if not configs:
            configs = {}
            Container.put("CellEditWdg:configs", configs)
        key = "%s" % (search_type)
        self.config = configs.get(key)
        if not self.config:

            # create one
            view = "edit"

            self.config = WidgetConfigView.get_by_search_type(search_type, view)
            configs[key] = self.config

            # get the base configs
            if config_xml:
                extra_config = WidgetConfig.get(view="edit", xml=config_xml)
                self.config.get_configs().insert(0, extra_config)

            # add an override if it exists
            view = "edit_item"
            #view = "test_edit"

            db_config = WidgetDbConfig.get_by_search_type(search_type, view)
            if db_config:
                self.config.get_configs().insert(0, db_config)

        self.sobject = None


        # create the edit widget
        try:
            # FIXME: This doesn't look right.. the type can only be display or action, not edit
            self.display_wdg = self.config.get_widget(element_name, "edit")
        except ImportError as e:
            print("WARNING: create widget", str(e))
            self.display_wdg = SimpleTableElementWdg()
            self.display_wdg.add("No edit defined")



        state = self.kwargs.get('state')
        state['search_type'] = search_type
        if self.display_wdg:
            self.display_wdg.set_state(state)

            if layout_version == '1':
                self.add_edit_behavior(self.display_wdg)
			

        # find the type of this element
        self.element_type = self.config.get_type(element_name)
        if not self.element_type:
            # NOTE: this should be centralized!
            if element_name.endswith('_date'):
                self.element_type = 'date'
            elif element_name.endswith('_time'):
                self.element_type = 'time'

        # ask the edit widget!
        if not self.element_type:
            try:
                self.element_type = self.display_wdg.get_type()
            except AttributeError as e:
                pass
                

        # otherwise, base it on the database type
        if not self.element_type:
            self.element_type = SearchType.get_tactic_type(search_type, element_name)

        

    def add_edit_behavior(cls, widget):
        '''this is only applicable in the old TableLayoutWdg''' 
        # add some special behavior for certain widgets ... custom ones will
        # have to implement their own
        from pyasm.widget import SelectWdg

        # table rows have a right click context override ... allow edit widgets to force the default right
        # click contexxt menu in order to be able to copy, cut and paste using right click menu ...
        #
        widget.force_default_context_menu()
        

        if (isinstance(widget, SelectWdg) or isinstance(widget, DynByFoundValueSmartSelectWdg)):
            web = WebContainer.get_web()
            
             
            if web.is_IE():
                # TODO: the click event does not work for IE8.  There is still
                # an issue that select the previous value selects.  This
                # is lost somewhere.
                event = 'change'
                widget.add_behavior( { 'type': event,
                   'cbjs_action': 'spt.dg_table.edit_cell_cbk( bvr.src_el, spt.kbd.special_keys_map.ENTER);'} );
            else:
                event = 'click'
                widget.add_behavior( { 'type': event,
                   'cbjs_action': 'spt.dg_table.select_wdg_clicked( evt, bvr.src_el );' } )

            #behavior = {
            #    'type': 'keyboard',
            #    'kbd_handler_name': 'DgTableSelectWidgetKeyInput'
            #}
            #widget.add_behavior( behavior )

        elif (isinstance(widget, CheckboxWdg)):
            widget.add_event("onclick", "spt.dg_table.edit_cell_cbk( this, spt.kbd.special_keys_map.ENTER)" );
            behavior = {
                'type': 'keyboard',
                'kbd_handler_name': 'DgTableMultiLineTextEdit'
            }
            widget.add_behavior(behavior)
        elif (isinstance(widget, TextAreaWdg)):
           behavior = {
               'type': 'keyboard',
               'kbd_handler_name': 'DgTableMultiLineTextEdit'
           }
           widget.add_behavior( behavior )
          
        elif (isinstance(widget, TextWdg)):
           behavior = {
               'type': 'keyboard',
               'kbd_handler_name': 'DgTableMultiLineTextEdit'
           }
           widget.add_behavior(behavior)


    add_edit_behavior = classmethod(add_edit_behavior)


    def get_display_wdg(self):
        return self.display_wdg



    def get_element_type(self):
        return self.element_type

    #def get_dependent_attrs(self):
    #    return self.dependent_attrs

    def set_sobject(self, sobject):
        self.sobject = sobject



    def get_display(self):
        element_name = self.kwargs['element_name']

        div = DivWdg()
        div.set_id("CellEditWdg_%s" % element_name)
        div.add_class("spt_edit_widget")
        div.add_style("position: absolute")
        div.add_style("z-index: 50")
        div.add_attr("spt_element_name", element_name)

        if not element_name:
            return widget

        try:
            element_attrs = self.config.get_element_attributes(element_name)
            edit_script = element_attrs.get("edit_script")
            if edit_script:
                div.add_attr("edit_script", edit_script)

            display = self.display_wdg.get_buffer_display()
            div.add(display)
            #div.add(self.display_wdg)
        except Exception as e:
            print("WARNING in CellEditWdg: ", e)
            self.display_wdg = TextWdg(element_name)
            self.display_wdg.set_value('Error in widget')
          
            display = self.display_wdg.get_buffer_display()
            div.add(display)
            

        # NOTE: this seems redundant, buffer display is already called at
        # this point
        if not self.sobject:
            self.sobject = self.kwargs.get('sobject')
        self.display_wdg.set_sobject(self.sobject)

        return div



    def get_values(self):
        '''method to get a data structure which can be used to populate the
        widget on the client side.  Generally the widgets are drawn unpopulated,
        so this information is need to dynamically load the informations'''
        assert self.sobject

        column = self.get_column()

        values = {}

        # main element
        if self.sobject.has_value(column):
            value = self.sobject.get_value(column)
            if self.element_type == 'time' and value and isinstance(value, six.string_types):
                # FIXME: this should use date util
                try:
                    tmp, value = value.split(" ")
                except Exception as e:
                    value = "00:00:00"

            values['main'] = value

        return values


    def get_column(self):
        '''special method to get the column override to add the data to'''
        element_name = self.kwargs['element_name']
        display_options = self.config.get_display_options(element_name)
        column = display_options.get("column")
        if not column:
            column = element_name
        return column
        

        
class CellWdg(BaseRefreshWdg):

    def get_display(self):
        web = WebContainer.get_web()

        search_key = self.kwargs.get('search_key')
        cmd = CellCmd(search_key=search_key)
        Command.execute_cmd(cmd)

        search_key = SearchKey.build_by_sobject(cmd.sobject)

        div = DivWdg()
        div.add_attr("spt_search_key", search_key )

        # Don't need to return the value because the how row is refreshed
        #div.add(cmd.value)
        div.add("&nbsp;")

        return div


class CellCmd(Command):

    def get_title(self):
        return "Table Cell Edit"

    def execute(self):
        web = WebContainer.get_web()

        search_key = self.kwargs.get('search_key')
        self.sobject = Search.get_by_search_key(search_key)

        element_name = web.get_form_value("element_name")
        value = web.get_form_value(element_name)
        if not value:
            value = web.get_form_value("main")
        if not value:
            value = web.get_form_value("name")
        self.sobject.set_value(element_name, value)
        self.sobject.commit()

        self.description = "Changed attribute [%s]" % element_name

        self.value = value




class RowCmd(Command):
    def execute(self):
        web = WebContainer.get_web()

        search_key = self.kwargs.get('search_key')
        sobject = Search.get_by_search_key(search_key)

        element_name = web.get_form_value("element_name")
        value = web.get_form_value(element_name)
        if not value:
            value = web.get_form_value("main")
        if not value:
            value = web.get_form_value("name")
        sobject.set_value(element_name, value)
        sobject.commit()

        self.value = value






from pyasm.widget import BaseTableElementWdg

class RowSelectWdg(BaseTableElementWdg):
    '''The Table Element which contains just a checkbox for selection'''
    def __init__(self, table_id, name=None, value=None):
       # Require "table_id" to be specified ... must be unique per table
        super(RowSelectWdg, self).__init__(name, value)
        self.table_id = table_id

        # Needed for MMS_COLOR_OVERRIDE ...
        web = WebContainer.get_web()
        self.skin = web.get_skin()



    def handle_th(self, th, cell_idx=None):

        th.set_id("maq_select_header")
        th.add_looks('dg_row_select_box')
        th.add_behavior( {'type': 'select', 'add_looks': 'dg_row_select_box_selected'} )

        th.set_attr('col_idx', str(cell_idx))
        th.add_style('width: 30px')
        th.add_style('min-width: 30px')

        th.add_behavior( {'type': 'click_up', 'mouse_btn':'LMB', 'modkeys':'',
                          'target_class': ('%s_row_target' % self.table_id),
                          'cbjs_action': 'spt.dg_table.select_deselect_all_rows(evt, bvr)'} )



    def get_title(self):
        return "&nbsp;"


    def handle_tr(self, tr):
        sobject = self.get_current_sobject()
        tr.set_attr( "spt_search_key", SearchKey.build_by_sobject(sobject, use_id=True) )


    def handle_td(self, td):

        # handle drag of row
        td.add_class("SPT_DRAG_ROW")
        td.add_class("SPT_DTS")

        td.add_style('width: 30px')
        td.add_style('min-width: 30px')

        # set the color of the row select
        td.add_color("background-color", "background", -10)

        i = self.get_current_index()
        sobject = self.get_current_sobject()

        row_id_str = "%s_select_td_%s" % (self.table_id, str(i+1))
        
        # prevent insert/edit rows getting selected for select all functions
        if sobject.is_insert():
            td.add_class( 'SPT_ROW_NO_SELECT')

        td.add_class( 'SPT_ROW_SELECT_TD cell_left' )
        # add this to specify the parent table
        td.add_class( 'SPT_ROW_SELECT_TD_%s' % self.table_id)

        td.add_looks( 'dg_row_select_box' )
        td.add_behavior( {
            'type': 'select',
            'add_looks': 'dg_row_select_box_selected'
        } )
        td.set_id( row_id_str )

        # determine if the client OS is a TOUCH DEVICE
        web = WebContainer.get_web()
        is_touch_device = web.is_touch_device()

        if is_touch_device:
            pass
        else:
            # click with no modifiers does select single (i.e. deselects all others) if not already selected,
            # or do nothing if already selected (this is behavior found in Mac OS X Finder) ...
            #td.add_behavior( { 'type': 'click_up', 'cbjs_action': 'spt.dg_table.select_single_row_cbk( evt, bvr );' } )
            td.add_behavior( {
                'type': 'click_up',
                'cbjs_action': 'spt.dg_table.select_row( bvr.src_el );'
            } )

            # SHIFT_LMB ... does block select, behaves like Mac OS X Finder
            td.add_behavior( { 'type': 'click_up', 'modkeys': 'SHIFT',
                               'cbjs_action': 'spt.dg_table.select_rows_cbk( evt, bvr );' } )

            # CTRL_LMB ... toggle select
            td.add_behavior( { 'type': 'click_up', 'modkeys': 'CTRL',
                               'cbjs_action':  'spt.dg_table.select_row( bvr.src_el );' } )

            # Drag will allow the dragging of items from a table onto anywhere else!
            td.add_behavior( { 'type': 'smart_drag', 'drag_el': 'drag_ghost_copy',
                               'use_copy': 'true',
                               'use_delta': 'true', 'dx': 10, 'dy': 10,
                               'drop_code': 'DROP_ROW',
                               'cbjs_pre_motion_setup': 'if (spt.drop) {spt.dg_table_action.sobject_drop_setup( evt, bvr );}',
                               'copy_styles': 'background: #393950; color: #c2c2c2; border: solid 1px black;' \
                                                ' text-align: left; padding: 10px;'
                               } )

        td.set_attr("selected", "no")


    def get_display(self):
        x = DivWdg()
        x.add_style("min-width: 24px")
        x.add_style("width: 24px")

        sobject = self.get_current_sobject()
        if sobject.is_insert():
            icon = IconWdg("New", IconWdg.NEW)
            x.add_style("padding: 2 0 0 4")
            x.add(icon)
        else:
            x.add("&nbsp;")


        return x





class AddPredefinedColumnWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
            "element_names": "list of the element_names",
            "search_type": "search_type to list all the possible columns",
            "popup_id": "id to assign to the popup this widget creates",
            "target_id": "the id of the panel where the table is"
        }


    def get_columns_wdg(self, title, element_names, is_open=False, edit=False):

        # hardcode to insert at 3, this will be overridden on client side
        widget_idx = 3

        content_wdg = DivWdg()
        content_wdg.add_class("spt_columns")
        content_wdg.add_style("margin-bottom: 5px")
        content_wdg.add_style("font-size: 1.0em")

        web = WebContainer.get_web()
        browser = web.get_browser()


        title_wdg = DivWdg()
        content_wdg.add(title_wdg)
        title_wdg.add_style("padding: 10px 3px")
        #title_wdg.add_color("background", "background3")
        title_wdg.add_style("border-bottom", "solid 1px #DDD")
        title_wdg.add_color("color", "color")
        title_wdg.add_style("margin: 0px -10px 5px -10px")


        swap = SwapDisplayWdg.get_triangle_wdg(is_open)
        title_wdg.add(swap)

        title_wdg.add_class("hand")
        title_wdg.add(title)


        cbjs_action = '''
            var top = bvr.src_el.getParent('.spt_columns');
            var content = top.getElement('.spt_columns_list');
            spt.toggle_show_hide(content);
        '''


        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            %s
            %s
            ''' % (cbjs_action, swap.get_swap_script() )
        }
        title_wdg.add_behavior(behavior)
        swap.add_action_script(cbjs_action)


        title_wdg.add_style("margin-bottom: 3px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("font-size: 12px")

        elements_wdg = DivWdg()
        elements_wdg.add_class("spt_columns_list")
        content_wdg.add(elements_wdg)
        if not is_open:
            elements_wdg.add_style("display: none")



        #num_elements = len(element_names)
        #if num_elements > 10:
        #    elements_wdg.add_style("max-height: 200")
        #    elements_wdg.add_style("height: 200")
        #    elements_wdg.add_style("overflow-y: auto")
        #    elements_wdg.add_style("overflow-x: hidden")
        #elements_wdg.add_border()
        #elements_wdg.add_style("margin: -5 -11 10 -11")


        if not element_names:
            menu_item = DivWdg()
            menu_item.add("&nbsp;&nbsp;&nbsp;&nbsp;<i>-- None Found --</i>")
            elements_wdg.add(menu_item)
            return content_wdg

        search_type = self.kwargs.get("search_type")
        search_type_obj = SearchType.get(search_type)
        table = search_type_obj.get_table()
        project_code = Project.get_project_code()

        security = Environment.get_security()


        count = 0

        # column edit option pass-throughs
        edit_options = self.kwargs.get("edit_options")

        if isinstance(edit_options, six.string_types):
            try:
                # hack taken from gear_settings kwarg in ui.panel.BaseTableLayoutWdg
                edit_options = edit_options.replace("'", '"')
                edit_options = jsonloads(edit_options)
            except ValueError:
                edit_options = None
        if not isinstance(edit_options, dict):
            edit_options = None

        # column edit exclusions
        static_elements = self.kwargs.get("static_element_names") or []

        for element_name in element_names:

            count += 1

            menu_item = DivWdg(css='hand')
            menu_item.add_class("spt_column")
            menu_item.add_style("height: 28px")
            menu_item.add_style("display: flex")
            menu_item.add_style("align-items: center")
            menu_item.add_style("padding-left: 10px")
            menu_item.add_style("width: 100%")



            checkbox = CheckboxWdg("whatever")
            if browser == 'Qt':
                checkbox.add_style("margin: -3px 5px 8px 0px")
            else:
                checkbox.add_style("margin-top: 1px")
            # undo the click.. let the div bvr take care of the toggling
            checkbox.add_behavior({'type':'click', 'cbjs_action': 'bvr.src_el.checked=!bvr.src_el.checked;'})
            if element_name in self.current_elements:
                checkbox.set_checked()

            checkbox.add_style("height: 16px")
            checkbox = DivWdg(checkbox)
            checkbox.add_style("float: left")

            attrs = self.config.get_element_attributes(element_name)

            default_access = attrs.get("access")
            if not default_access:
                default_access = "allow"

            # check security access
            access_key2 = {
                'search_type': search_type,
                'project': project_code
            }
            access_key1 = {
                'search_type': search_type,
                'key': element_name, 
                'project': project_code

            }
            access_keys = [access_key1, access_key2]
            is_viewable = security.check_access('element', access_keys, "view", default=default_access)
            is_editable = security.check_access('element', access_keys, "edit", default=default_access)
            if not is_viewable and not is_editable:
                continue



            help_alias = attrs.get("help");
            if help_alias:
                menu_item.add_attr("spt_help", help_alias)
            else:
                menu_item.add_attr("spt_help", "%s_%s" % (table, element_name))


            title = attrs.get("title")
            if not title:
                title = Common.get_display_title(element_name)
            title = title.replace("\n", " ")
            title = title.replace("\\n", " ")

            if title.find("->") != -1:
                parts = title.split("->")
                title = parts[1]


            if len(title) > 45:
                title = "%s ..." % title[:42]
            else:
                title = title


            #full_title = "%s &nbsp; <i style='opacity: 0.3; font-size: 0.8em'>(%s)</i>" % ( title, element_name)
            #display_title = full_title
            full_title = "%s (%s)" % ( title, element_name)
            display_title = title
            menu_item.add_attr("title", full_title)

            

            target = self.kwargs.get("target") or None

            #menu_item.add_attr("title", full_title)

            menu_item.add(checkbox)
            menu_item.add("&nbsp;&nbsp;")
            menu_item.add(display_title)

            menu_item.add_behavior({
            'type': "click_up", 
            'target_id': self.target_id,
            'target': target,
            'element_name': element_name,
            'widget_idx': widget_idx,
            'cbjs_action': '''

            var panel;

            var popup = bvr.src_el.getParent(".spt_popup");

            if (bvr.target) {
                var parent = bvr.src_el.getParent("."+bvr.target);
                panel = parent.getElement(".spt_layout");
            }
            else if (popup) {
                var panel = popup.panel;
                if (!panel) {
                    var activator = popup.activator;
                    if (activator) {
                        panel = activator.getParent(".spt_layout");
                    }
                }
            }
            if (!panel) {
                panel = document.id(bvr.target_id);
            }


            if (!panel) {
                spt.alert('Please re-open the Column Manager');
                return;
            }
            var table = panel.getElement(".spt_table");
            spt.dg_table.toggle_column_cbk(table,bvr.element_name,bvr.widget_idx);
            cb = bvr.src_el.getElement('input[type=checkbox]');
            cb.checked=!cb.checked;
            '''
            })


            # mouse over colors
            color = content_wdg.get_color("background", -15)
            menu_item.add_event("onmouseover", "this.style.background='%s'" % color)
            menu_item.add_event("onmouseout", "this.style.background=''")

            menu_item_container = DivWdg()
            elements_wdg.add(menu_item_container)
            menu_item_container.add(menu_item)

            if (edit in ['true', True]) and (element_name not in static_elements):

                button = IconButtonWdg(name="Edit", icon="FA_EDIT")
                menu_item_container.add(button)
                button.add_behavior( {
                'type': 'click_up',
                'target_id': self.target_id,
                'target': target,
                'element_name': element_name,
                'edit_options': edit_options or {},
                'cbjs_action': '''

                var panel;

                var popup = bvr.src_el.getParent(".spt_popup");

                if (bvr.target) {
                    var parent = bvr.src_el.getParent("."+bvr.target);
                    panel = parent.getElement(".spt_layout");
                }
                else if (popup) {
                    var panel = popup.panel;
                    if (!panel) {
                        var activator = popup.activator;
                        if (activator) {
                            panel = activator.getParent(".spt_layout");
                        }
                    }
                }
                if (!panel) {
                    panel = document.id(bvr.target_id);
                }


                if (!panel) {
                    spt.alert('Please re-open the Column Manager');
                    return;
                }
                var table = panel.getElement(".spt_table");

                var class_name = 'tactic.ui.manager.ElementDefinitionWdg'
                var popup_id = 'edit_column_defn_wdg';
                var title =  'Edit Column Definition';

                var element_name = bvr.element_name;
                var view = table.getAttribute("spt_view");
                var search_type = table.getAttribute("spt_search_type");

                var args = {
                    'search_type': search_type,
                    'view': view,
                    'element_name': element_name,
                    'is_insert': "false"
                };
                var edit_options = bvr.edit_options;

                for (var key in edit_options) {
                    args[key] = edit_options[key];
                }

                spt.panel.load_popup(title, class_name, args=args);
                '''
                } )

            menu_item_container.add_style("display: flex")
            menu_item_container.add_style("justify-content: space-between")
            menu_item_container.add_style("align-items: center")
            menu_item_container.add_class("spt_column_container")
            menu_item_container.add_attr("spt_element_name", element_name)
            elements_wdg.add(menu_item_container)

        if not count:
            return None


        return content_wdg




    def get_display(self):
        # top container is a panel
        container = self.top
        self.set_as_panel(container)
        top = DivWdg()
        container.add(top)


        width = self.kwargs.get("width") or 400
        top.add_style("width: %spx" % width)

        search_type = self.kwargs.get("search_type")
        search_type_obj = SearchType.get(search_type)


        self.current_elements = self.kwargs.get('element_names')
        if not self.current_elements:
            self.current_elements = []
        else:
            if isinstance(self.current_elements, six.string_types):
                self.current_elements = self.current_elements.split(",")


        # for testing purposes
        is_admin = self.kwargs.get("is_admin")
        if is_admin in ['false', False]:
            self.is_admin = False
        else:
            self.is_admin = Environment.get_security().is_admin()



        self.extra_elements = self.kwargs.get("extra_element_names")
        if self.extra_elements:
            if isinstance(self.extra_elements, six.string_types):
                self.extra_elements = self.extra_elements.split(",")
            self.all_element_names = self.current_elements[:]
            self.all_element_names.extend(self.extra_elements)
        else:
            self.all_element_names = []



        self.target_id = self.kwargs.get("target_id")



        # hardcode to insert at 3, this will be overridden on client side
        widget_idx = 3

        top.add_color("background", "background")
        top.add_border()

        # shelf widget sholuld only be seen by admin
        if self.is_admin:

            shelf_wdg = DivWdg()
            top.add(shelf_wdg)
            shelf_wdg.add_style("padding: 5px 5px 0px 5px")



            from tactic.ui.app import HelpButtonWdg
            help_button = HelpButtonWdg(alias='main')
            shelf_wdg.add(help_button)
            help_button.add_style("float: right")



            from tactic.ui.widget import ActionButtonWdg
            add_button = ActionButtonWdg(title="Add")
            shelf_wdg.add(add_button)
            shelf_wdg.add("<br clear='all'/>")

            title = self.kwargs.get("title")
            add_button.add_behavior( {
                'type': 'click_up',
                'title': title,
                'search_type': search_type,
                'cbjs_action': '''
                var class_name = 'tactic.ui.startup.column_edit_wdg.ColumnEditWdg';
                var kwargs = {
                    search_type: bvr.search_type
                }
                spt.panel.load_popup(bvr.title, class_name, kwargs);
                '''
            } )



        context_menu = DivWdg()
        top.add(context_menu)
        context_menu.add_class("spt_column_manager")

        context_menu.add_style("padding: 0px 10px 10px 10px")
        #context_menu.add_border()
        context_menu.add_color("color", "color")
        context_menu.add_style("max-height: 500px")
        context_menu.add_style("overflow-y: auto")
        context_menu.add_style("overflow-x: hidden")


        element_view = self.kwargs.get("element_view") or "definition"
        self.config = WidgetConfigView.get_by_search_type(search_type, element_view)

        predefined_element_names = ['preview', 'edit_item', 'delete', 'notes', 'notes_popup', 'task', 'task_edit', 'task_schedule', 'task_pipeline_panels', 'task_pipeline_vertical', 'task_pipeline_report', 'task_status_history', 'task_status_summary', 'completion', 'file_list', 'group_completion', 'general_checkin_simple', 'general_checkin', 'explorer', 'show_related', 'detail', 'notes_sheet', 'work_hours', 'history', 'summary', 'metadata']
        predefined_element_names.sort()

        # define a finger menu
        #finger_menu, menu = self.get_finger_menu()
        #context_menu.add(finger_menu)

        ##menu.set_activator_over(context_menu, "spt_column", top_class='spt_column_manager', offset={'x':10,'y':0})
        #menu.set_activator_out(context_menu, "spt_column", top_class='spt_column_manager')



        defined_element_names = []
        for config in self.config.get_configs():
            #if config.get_view() not in ['definition', 'default_definition']:
            if config.get_view() != 'definition':
                continue
            file_path = config.get_file_path()
            #if file_path == 'generated':
            if file_path and file_path.endswith("DEFAULT-conf.xml") or file_path == 'generated':
                continue

            element_names = config.get_element_names()

            for element_name in element_names:

                if element_name not in defined_element_names:
                    defined_element_names.append(element_name)


        column_info = SearchType.get_column_info(search_type)
        columns = column_info.keys()
        for column in columns:
            if column == 's_status':
                continue

            if column not in defined_element_names:
                defined_element_names.append(column)



        # Add custom layout widgets
        search = Search("config/widget_config")
        search.add_filter("widget_type", "column")
        configs = search.get_sobjects()
        if configs:
            config_element_names = [x.get_value("view") for x in configs]

            defined_element_names.extend(config_element_names)


        # remove duplicate elements
        self.all_element_names = list(set(self.all_element_names))

        edit = self.kwargs.get("edit") in [True, "true"]
        if self.all_element_names:
            self.all_element_names.sort()
            title = 'Columns'
            context_menu.add( self.get_columns_wdg(title, self.all_element_names, is_open=True, edit=edit) )

        else:
            defined_element_names.sort()
            title = 'Columns'
            context_menu.add( self.get_columns_wdg(title, defined_element_names, is_open=True, edit=edit) )




        # add custom elements for the job
        if search_type == "workflow/job":
            search = Search("workflow/job_type")
            job_types = search.get_sobjects()

            for job_type in job_types:
                data = job_type.get_json_value("data") or {}
                if isinstance(data, six.string_types):
                    data = jsonloads(data)
                form_extra_data = data.get("form_extra_data") or {}
                if not form_extra_data:
                    continue
                if isinstance(form_extra_data, six.string_types):
                    form_extra_data = jsonloads(form_extra_data)
                components = form_extra_data.get("components") or []
                job_type_elements = []
                for component in components:
                    component_type = component.get("type")
                    if component_type in ['button','signature','columns']:
                        continue
                    label = component.get("label")
                    key = component.get("key")
                    job_type_elements.append(key)
                if job_type_elements:
                    context_menu.add( self.get_columns_wdg(job_type.get_value("name"), job_type_elements))

        # Add predefined columns

        show_builtin_columns = self.kwargs.get("show_builtin_columns")

        # admin site will always show all builtin
        if self.is_admin or show_builtin_columns in [True, 'true']:
            def_db_config = WidgetDbConfig.get_by_search_type("ALL", "definition")
            if def_db_config:
                element_names = def_db_config.get_element_names()
                predefined_element_names.extend(element_names)

            title = "Built-in Columns"
            context_menu.add( self.get_columns_wdg(title, predefined_element_names) )



        # schema defined columns for foreign keys
        """
        element_names = []
        view_schema_columns = True
        if view_schema_columns:

            # get the database columns
            schema = Schema.get()
            xml = schema.get_xml_value("schema")
            connects = xml.get_nodes("schema/connect[@from='%s']" % search_type)


            for connect in connects:
                to_search_type = Xml.get_attribute(connect, 'to')
                to_search_type_obj = SearchType.get(to_search_type, no_exception=True)
                if not to_search_type_obj:
                    continue


                column = Xml.get_attribute(connect, 'from_col')
                implied_foreign_key = False
                if not column:
                    column = SearchType.get_foreign_key(to_search_type)
                    implied_foreign_key = True


                element_names.append(column)


            #context_menu.add(HtmlElement.br())
            #title = "Schema Columns"
            #context_menu.add( self.get_columns_wdg(title, element_names) )
        """


 
 

        # check to see if the user is allowed to add db_columns
        default = "deny"
        group = "db_columns"

        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):

            # get the database columns
            column_info = SearchType.get_column_info(search_type)
            columns = list(column_info.keys())

            columns.sort()
            context_menu.add( self.get_columns_wdg("Database Columns", columns) )

 
        #popup_wdg.add(context_menu, "content")
        #return popup_wdg

        if self.kwargs.get("is_refresh"):
            return top
        else:
            return container


    def get_finger_menu(self):

        # handle finger menu
        top_class = "spt_column_manager"
        from tactic.ui.container import MenuWdg, MenuItem
        menu = MenuWdg(mode='horizontal', width = 25, height=20, top_class=top_class)


        menu_item = MenuItem('action', label=IconWdg("Show Help", IconWdg.HELP_BUTTON))
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            if (!spt.help) return;
            spt.help.set_top();
            var menu = spt.table.get_edit_menu(bvr.src_el);
            var activator = menu.activator_el; 
            var help_alias = activator.getAttribute("spt_help");
            spt.help.load_alias(help_alias);
            '''
        } )

        # finger menu container
        widget = DivWdg()
        widget.add_class(top_class)
        widget.add_styles('position: absolute; display: none; z-index: 1000')
        widget.add(menu)

        return widget, menu

 





class EditColumnDefinitionWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
            "search_type": "search_type to list all the possible columns",
            "view": "view of the config",
            "element_name": "name of the element_name",
            "popup_id": "id to assign to the popup this widget creates",
            "refresh": "is this a refresh"
        }




    def set_as_panel(self, widget):
        widget.add_class("spt_panel")

        widget.add_attr("spt_class_name", Common.get_full_class_name(self) )
        for name, value in self.kwargs.items():
            widget.add_attr("spt_%s" % name, value)

       


    def init(self):
        self.error = None
        refresh = self.kwargs.get("refresh")



    def get_display(self):

        search_type = self.kwargs.get("search_type")
        view = self.kwargs.get("view")
        
        element_name = self.kwargs.get("element_name")
        refresh = self.kwargs.get("refresh")

      

        widget = DivWdg()   
        # get the definition of the config element
        # try the db first
        config_view = WidgetConfigView.get_by_search_type(search_type, view)
        node = config_view.get_element_node(element_name, True) 
       
        if not node:
            config_string = "<No definition>"
        else:
            config_string = config_view.get_xml().to_string(node)

        content_wdg = DivWdg()

        if self.error:
            content_wdg.add(self.error)

        content_wdg.set_id("EditColumnDefinitionWdg_panel")
        self.set_as_panel(content_wdg)

        # display definition
        content_wdg.add("Table Display")
        content_wdg.add("<br/>")
        text = TextAreaWdg('display_definition')
        text.set_option("rows", "10")
        text.set_option("cols", "65")
        text.set_value(config_string)
        content_wdg.add(text)


        # get the EDIT definition of the config element
        config_view = WidgetConfigView.get_by_search_type(search_type, "edit")
        node = config_view.get_element_node(element_name, True)
        if not node:
            config_string = "<No definition>"
        else:
            config_string = config_view.get_xml().to_string(node)


        content_wdg.add("<br/><br/>")

        # edit definition
        content_wdg.add("<br/>")

        swap = SwapDisplayWdg.get_triangle_wdg()
        text = TextAreaWdg('edit_definition')

        # if it is not processed in the Cbk, may as well grey it out
        text.add_class('look_smenu_disabled')
        text.set_option("rows", "10")
        text.set_option("cols", "65")
        text.set_value(config_string)

        title = SpanWdg('Edit Panel Display (View only)')
        div = DivWdg(text)
        SwapDisplayWdg.create_swap_title(title, swap, div)
        content_wdg.add(swap)
        content_wdg.add(title)
        content_wdg.add(div)

        #switch = DivWdg()
        #switch.add("Switch all others [%s] columns?" % element_name)
        #content_wdg.add(switch)
        content_wdg.add( HtmlElement.hr() )
        
        behavior_edit = {
            'type': 'click_up',
            'cbjs_action': 'spt.dg_table_action.edit_definition_cbk(evt, bvr)',
            'options': {
                'search_type': search_type,
                'element_name': element_name
            }
            #'values': "spt.api.Utility.get_input(spt.popup.get_popup(bvr.src_el) , 'save_view');"

           

        }
        behavior_cancel = {
            'type': 'click_up',
            'cbjs_action': "spt.popup.destroy( spt.popup.get_popup( bvr.src_el ) );"
        }
        button_list = [{'label':  "Save" , 'bvr': behavior_edit},
                {'label':  "Cancel", 'bvr': behavior_cancel}]        
        edit_close = TextBtnSetWdg( buttons=button_list, spacing =6, size='large', \
                align='center',side_padding=10)

       
        default_view = 'definition'
        select=  SelectWdg('save_view', label='Save for: ')
        select.set_persist_on_submit()
        select.add_empty_option('-- Select --', '')
        select.set_option('labels', [default_view, 'current view'])
        select.set_option('values',[default_view,view])

        content_wdg.add(select)

        from pyasm.widget import HintWdg
        help = HintWdg('If saved for definition, it affects the display in all the views for this search type.')
        content_wdg.add(help)
        content_wdg.add(HtmlElement.br(2))
        content_wdg.add(edit_close)

        # FIXME: is there a way to avoid this??
        if refresh:
            return content_wdg

        
        widget.add(content_wdg)

        return widget



class EditColumnDefinitionCbk(Command):

    def get_title(self):
        return "Edit Column Definition"

    def execute(self):
        search_type = self.kwargs.get('search_type')
        element_name = self.kwargs.get('element_name')
        #view = self.kwargs.get('view')

        search_type = SearchType.get(search_type).get_base_key()

        web = WebContainer.get_web()
        display_config = web.get_form_value("display_definition")
        save_view = web.get_form_value("save_view")

        default_view = "definition"
        if not save_view:
            save_view = default_view
        # FIXME: taken from client API (set_config_definition() )
        # ... should centralize
        config_search_type = "config/widget_config"
        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", save_view)
        config = search.get_sobject()
        if not config:
            if save_view != 'definition':
                # raise exception 'cuz the user should save out a view first
                raise UserException('You should save out a view first before editing the column definition for this specific view [%s]' % save_view)

            config = SearchType.create(config_search_type)
            config.set_value("search_type", search_type )
            config.set_value("view", save_view )

            # create a new document
            xml = Xml()
            xml.create_doc("config")
            root = xml.get_root_node()
            view_node = xml.create_element( save_view )
            #root.appendChild(view_node)
            xml.append_child(root, view_node)

            config.set_value("config", xml.to_string())
            
            config._init()


        # update the definition
        config.append_xml_element(element_name, display_config)
            
        config.commit_config()

        self.add_description("Saved column definition [%s] for [%s] in view [%s]" %(element_name, search_type, save_view)) 
        # update the edit definition
        #edit_definition = web.get_form_value("edit_definition")
        #edit_view = "edit_definition"
        #edit_config = self.get_config(search_type, edit_view)
        #edit_config.append_xml_element(element_name, edit_definition)
        #edit_config.commit_config()



    def get_config(self, search_type, view):

        # FIXME: taken from client API (set_config_definition() )
        # ... should centralize
        config_search_type = "config/widget_config"
        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", view)
        config = search.get_sobject()
        if not config:
            

            config = SearchType.create(config_search_type)
            config.set_value("search_type", search_type )
            config.set_value("view", view )

            # create a new document
            xml = Xml()
            xml.create_doc("config")
            root = xml.get_root_node()
            view_node = xml.create_element(view)
            #root.appendChild(view_node)
            xml.append_child(root, view_node)

            config.set_value("config", xml.to_string())
            config._init()

        return config


