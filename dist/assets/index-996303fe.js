import{Y as t}from"./index-d300417d.js";import{l as e,a as s}from"./url-2799ff3c.js";const a=t("HomeModule",{state(){return{navBool:!1,book_list:[]}},actions:{SET_NAC_BOOL(){this.navBool=!this.navBool},get_book_list(){e(s.book_list,"get").then(o=>{this.book_list=o.data.data}).catch(o=>{console.log(o)})}}}),i=t("sectionModule",{state(){return{dialogFormVisible:!1,id:0,scetion_obj:{}}}}),l=t("tagsModule",{state(){return{dialogFormVisible:!1,tags_obj:{}}}});function u(){return{home:a(),section:i(),tags:l()}}export{u};