import React from 'react';

import { BpmnDocumentModel, BpmnElementType, EditorDocument, EditorDocumentModel, Pane, PaneComponentProps, PaneHeader, PaneProvider } from '@atlas-engine/atlas_studio_sdk';
import { BpmnDocumentOverlay } from '@atlas-engine/atlas_studio_sdk/out/types/bpmn/BpmnDocumentOverlays';

import { PropertiesRobotTaskPaneContent } from './PropertiesRobotTaskPaneContent';

// this function overrids internal studio functions. It is not recommended to do this, but it is the only way to add an custom overlay to the bpmn editor
function addRobotIconOverlay(editorDocumentModel: BpmnDocumentModel) {
  editorDocumentModel.overlays.update = (overlays: BpmnDocumentOverlay[]): void => {
    (editorDocumentModel as any).overlays.removeAll();

    const icons = overlays.filter((overlay) => overlay.type === 'icon') as any[];
    icons.forEach((icon) => (editorDocumentModel as any).overlays.addIcon(icon.elementId, icon.icon, icon.subtype, icon.position));

    const covers = overlays.filter((overlay) => overlay.type === 'cover') as any[];

    const externalTasks = (editorDocumentModel as BpmnDocumentModel).elements.getAllElements()?.filter(element => element.type === BpmnElementType.ExternalServiceTask) ?? [];

    const robotTasks = externalTasks.filter(task => {
      const customType = task.customProperties?.find(prop => prop.name === 'studio.externalTask.customType');
      console.log('customType', customType);
      return customType?.value === 'robot';
    });

    robotTasks.forEach((task) => {
      (editorDocumentModel as any).overlays.addReactElementOverlay(task.id, <img width='20px' src='data:image/png;base64,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' />, { top: 2, left: 25 });
    });

    covers.forEach((cover) => (editorDocumentModel as any).overlays.addCover(cover.element, cover.studio));
  }
}

function shouldPaneBeDisplayed(editorDocument: EditorDocument, editorDocumentModel: EditorDocumentModel): boolean {
  if (editorDocument?.documentType !== 'bpmn') {
    return false;
  }

  const selectedElement = (editorDocumentModel as BpmnDocumentModel)?.selection?.getOnlyElementOrNull();

  if (editorDocumentModel !== null) {
    addRobotIconOverlay(editorDocumentModel as any);
  }

  const isExternalServiceTask = selectedElement?.type === BpmnElementType.ExternalServiceTask;

  if (!isExternalServiceTask) {
    return false;
  }

  const customExternalTaskType = selectedElement?.customProperties?.find(
    (customProperty) => customProperty.name === 'studio.externalTask.customType'
  )?.value;

  const isRobotExternalTask = customExternalTaskType === 'robot';

  return isRobotExternalTask;
}

function PaneFull(props: PaneComponentProps): JSX.Element {
  return (
    <Pane>
      <PaneHeader
        className='pane-header--hero'
        collapsed={props.collapsed}
        paneId={props.paneId}
        studio={props.studio}
        title='Robot Service Task'
      />
      {!props.collapsed &&
        <PropertiesRobotTaskPaneContent {...props} />
      }
    </Pane>
  );
}

export const paneProvider: PaneProvider = {
  getPaneTitle: () => 'Robot Service Task',
  shouldBeDisplayed: shouldPaneBeDisplayed,
  Pane: PaneFull,
  PaneContent: PropertiesRobotTaskPaneContent,
};
