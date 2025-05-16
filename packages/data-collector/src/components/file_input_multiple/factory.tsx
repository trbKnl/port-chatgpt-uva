import { 
    PromptFactory,
    ReactFactoryContext 
} from "@eyra/feldspar"
import { FileInputMultiple } from "./file_input_multiple"
import { PropsUIPromptFileInputMultiple } from "./types"

export class FileInputMultipleFactory implements PromptFactory {
  create(body: unknown, context: ReactFactoryContext) {
    if (this.isBody(body)) {
      return <FileInputMultiple {...body} {...context} />;
    }
    return null;
  }

  private isBody(body: unknown): body is PropsUIPromptFileInputMultiple {
    return (
      (body as PropsUIPromptFileInputMultiple).__type__ === "PropsUIPromptFileInputMultiple"
    );
  }
}

