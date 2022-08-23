import React from 'react';

import { EditorDocument, PaneComponentProps, PaneProvider, EditorDocumentModel } from '@atlas-engine/atlas_studio_sdk';
import { Studio } from '@atlas-engine/atlas_studio_sdk';

import {
  Pane,
  PaneBody,
  PaneHeader,
  PaneHeaderHelpIcon,
  PaneProperty,
  SelectOption,
} from '@atlas-engine/atlas_studio_sdk';

import { assertNotNull } from '@atlas-engine/atlas_studio_sdk';

const selectOptions: SelectOption[] = [
  { value: "none", label: 'None' },
  { value: "external", label: 'External Task' },
  { value: "http", label: 'HTTP Service Task' },
];

export const paneProvider: PaneProvider = {
  getPaneTitle: getPaneTitle,
  shouldBeDisplayed: shouldBeDisplayed,
  Pane: PaneFull,
  PaneContent: PaneContent,
};

function getPaneTitle(): string {
  return 'Service Task';
}

function PaneFull(props: PaneComponentProps): JSX.Element {
  return (
    <Pane>
      <PaneHeader studio={props.studio} title={getPaneTitle()} paneId={props.paneId} collapsed={props.collapsed}>
        <PaneHeaderHelpIcon studio={props.studio} id="bpmn/properties/robot_task" />
      </PaneHeader>
      {props.collapsed !== true && <PaneContent {...props} />}
    </Pane>
  );
}

function shouldBeDisplayed(editorDocument: EditorDocument, editorDocumentModel: any, studio: Studio): boolean {
  return (
    shouldBeDisplayedForBpmnElementOfType(editorDocument, editorDocumentModel, "robot")
  );
}

function PaneContent(props: PaneComponentProps): JSX.Element | null {
  const selection = getBpmnSelectionForPropertiesPane(props);

  if (selection == null) {
    return null;
  } else {
    return <RobotTaskServicePane key={getKeyForPropertiesPane(selection)} {...props} />;
  }
}

function RobotTaskServicePane(props: PaneComponentProps): JSX.Element {
  const bpmnDocumentModel: any | null = props.editorDocumentModel; // any => BpmnDocumentModel
  assertNotNull(bpmnDocumentModel, 'bpmnDocumentModel');

  const element = bpmnDocumentModel.selection.getOnlyElementOrNull();
  //assertBpmnElementIsServiceTask(element);

  const updateServiceTaskType = (serviceTaskType: any): void => {
    bpmnDocumentModel.elements.setElementProperty(element.id, 'serviceTaskType', serviceTaskType);
  };

  const initialValue = selectOptions.find((option) => option.value === element.serviceTaskType);

  return (
    <PaneBody>
      <PaneProperty
        key={`element_service_task_type_${element.serviceTaskType}`}
        htmlId="service-task-type"
        label="Type"
        type="select"
        options={selectOptions}
        value={initialValue}
        onChange={(newValue: any) => updateServiceTaskType(newValue.value)}
      />
    </PaneBody>
  );
}


export function shouldBeDisplayedForBpmnElementOfType(
  editorDocument: EditorDocument,
  editorDocumentModel: EditorDocumentModel,
  selectionType: string
): boolean {
  if (editorDocument?.documentType !== 'bpmn') { // BPMN_DOCUMENT_TYPE == 'bpmn'
    return false;
  }

  const selectedElements = (editorDocumentModel as any)?.selection?.getElements();

  return selectedElements?.length === 1 && selectedElements[0]?.type === selectionType;
}

export function getBpmnSelectionForPropertiesPane(props: PaneComponentProps): any[] | null {
  const editorDocument: EditorDocument = props.editorDocument;
  const bpmnDocumentModel: any | null = props.editorDocumentModel; // BpmnDocumentModel

  if (
    editorDocument == null ||
    editorDocument.modelKey != 'BpmnDocumentModel' ||
    bpmnDocumentModel == null ||
    !bpmnDocumentModel.isReadyForInteraction()
  ) {
    return null;
  }

  const selection = bpmnDocumentModel.selection.getElements();
  if (selection.length === 0) {
    return null;
  }

  return selection;
}

export function getKeyForPropertiesPane(selection: any[]): string {
  const selectedElement = selection[0];
  assertNotNull(selectedElement, 'selectedElement');

  return `${selectedElement.type}__${selectedElement.id}__${selectedElement.name}`;
}



