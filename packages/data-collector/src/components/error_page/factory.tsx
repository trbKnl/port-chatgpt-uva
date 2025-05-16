import { 
    PromptFactory,
    ReactFactoryContext 
} from "@eyra/feldspar"
import { ErrorPage } from "./error_page"
import { PropsUIPageError } from "./types"

export class ErrorPageFactory implements PromptFactory {
  create(body: unknown, context: ReactFactoryContext) {
    if (this.isBody(body)) {
      return <ErrorPage {...body} {...context} />;
    } 
    return null;
  }

  private isBody(body: unknown): body is PropsUIPageError {
    return (
      (body as PropsUIPageError).__type__ === "PropsUIPageError"
    );
  }
}

