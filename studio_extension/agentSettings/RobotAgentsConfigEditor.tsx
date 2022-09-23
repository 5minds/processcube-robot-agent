import {
  Editor,
  EditorContent,
  EditorDocumentRendererProps,
  OneLineCodeEditor,
  Studio,
  assertNotNull,
} from '@atlas-engine/atlas_studio_sdk';
import React from 'react';
import { v4 as uuidv4 } from 'uuid';

import { RobotAgentsConfigDocument } from './RobotAgentsConfigDocument';
import '../styles.scss';
import { RobotAgent } from './getRobotAgents';

export class RobotAgentsConfigEditor extends React.Component<EditorDocumentRendererProps, any> {
  private studio: Studio;
  private model: RobotAgentsConfigDocument | null = null;

  constructor(props: EditorDocumentRendererProps) {
    super(props);
    this.studio = props.studio;
  }

  async componentDidMount(): Promise<void> {
    this.model = await this.studio.editors.getEditorDocumentModel(this.props.editorDocument);
    this.forceUpdate();
  }

  private onDataChanged(values: Array<RobotAgent>, modifiedAgent: RobotAgent): void {
    // This is one of those situations where the TypeScript compiler complains about `this.model` possibly being `null`,
    // but you know this can't possibly be `null` because this method can only ever be called if the model is present.
    //
    // `assertNotNull` provides a utility function to both appease the compiler and give you the peace of mind that
    // if - for some unforeseen reason or future implementation change - `this.model` is `null` at this point, we fail
    // early and with a descriptive error message (which is why this is preferable to the bang operator).
    assertNotNull(this.model, 'this.model');

    const agents = [...values.filter(agent => agent.uuid !== modifiedAgent.uuid), modifiedAgent].filter(agent => agent.name.length > 0 || agent.url.length > 0);

    this.model.setValue({ agents });
  }

  render(): JSX.Element | null {
    if (this.model == null) {
      return null;
    }

    const agents = [...this.model.getValue().agents, { uuid: uuidv4(), name: '', url: '' }];

    return (
      <Editor>
        <EditorContent>
          <div style={{ margin: '20px' }}>
            <h2>Robot Agents</h2>
            <div style={{ display: 'grid', rowGap: '10px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', columnGap: '10px' }}>
                <span>Name</span>
                <span>URL</span>
              </div>
              {
                agents.map((agent, index) => <AgentEditor key={index} agent={agent} studio={this.props.studio} onChange={(agent) => this.onDataChanged(agents, agent)} />)
              }
            </div>
          </div>
        </EditorContent>
      </Editor>
    );
  }
}

function AgentEditor(props: { agent: RobotAgent, onChange: (agent: RobotAgent) => void, studio: Studio }): JSX.Element {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', columnGap: '20px' }}>
      <OneLineCodeEditor
        initialValue={props.agent.name}
        language='text'
        onChange={(value) => props.onChange({ ...props.agent, name: value })}
        studio={props.studio}
      />
      <OneLineCodeEditor
        initialValue={props.agent.url}
        language='text'
        onChange={(value) => props.onChange({ ...props.agent, url: value })}
        studio={props.studio}
      />
    </div>
  );
}
