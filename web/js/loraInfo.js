import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

app.registerExtension({
    name: "ycyy.LoraInfo",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeType?.comfyClass == "LoraInfo") {
            const original_getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
            nodeType.prototype.getExtraMenuOptions = function (_, options) {
                const widget = this.widgets[0];
                original_getExtraMenuOptions?.apply(this, arguments);
                options.unshift({
                    content: "Lora Info Online",
                    callback: async () => {                       
                        onlineInfo(widget,nodeData)
                    }
                })
            }
        }
    }
})
function onlineInfo(widget,nodeData) {
    const body = new FormData();  
    body.append('lora_name',widget.value);
    api.fetchApi(
        "/ycyy/getLoraData", 
        {
            method: "POST",
            body,
        }
    )
    .then(response => response.text())
    .then(data=>{
        const lora_info = JSON.parse(data).data;
        if(lora_info!=null){          
            const url = lora_info.url;
            if(url!=null){
                window.open(url,"_blank");
            }
        }
        else{
            app.extensionManager.toast.add({
                severity: 'error',
                summary: 'error!',
                detail: 'No lora information found!',
                life: 3000
            });
            
        }     
    });
}