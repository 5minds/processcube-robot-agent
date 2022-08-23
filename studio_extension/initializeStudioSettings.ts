import { Studio } from '@atlas-engine/atlas_studio_sdk';

export function initializeDefaultSettings(studio: Studio): void {

    console.log("Initializing default settings...");

    /*
    studio.settings.registerDefaults({
        "processcube.robot.extension": {
            "agents": [
              {
                "name": "ERP SAP [PRD]",
                "url": "https://erp-sap.prd.5minds.cloud:4712/robot_agents/robots"
              },
              {
                "name": "MES SAP [PRD]",
                "url": "https://mes-sap.prd.5minds.cloud:4712/robot_agents/robots"
              }
            ]
          }
    });
    */

    // backup for using registerDefaults() won't visible in Studio settings
    // see: https://github.com/atlas-engine/AtlasStudio/issues/1261
    try {
        const settings = studio.settings.get('processcube.robot.extension');
        console.log(settings);
    } catch {
        studio.settings.set("processcube.robot.extension", {
            "agents": [
                {
                  "name": "ERP SAP [PRD]",
                  "url": "https://erp-sap.prd.5minds.cloud:4712/robot_agents/robots"
                },
                {
                  "name": "MES SAP [PRD]",
                  "url": "https://mes-sap.prd.5minds.cloud:4712/robot_agents/robots"
                }
              ]
        });    
    }
}
