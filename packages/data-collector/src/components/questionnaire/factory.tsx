import { 
    PromptFactory,
    ReactFactoryContext 
} from "@eyra/feldspar"
import { Questionnaire } from "./questionnaire"
import { PropsUIPromptQuestionnaire } from "./types"

export class QuestionnaireFactory implements PromptFactory {
  create(body: unknown, context: ReactFactoryContext) {
    if (this.isBody(body)) {
      return <Questionnaire {...body} {...context} />;
    }
    return null;
  }

  private isBody(body: unknown): body is PropsUIPromptQuestionnaire {
    return (
      (body as PropsUIPromptQuestionnaire).__type__ === "PropsUIPromptQuestionnaire"
    );
  }
}

