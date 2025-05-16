import { DataSubmissionPageFactory, ScriptHostComponent } from "@eyra/feldspar";
import { ConsentFormVizFactory } from "./factories/consent_form_viz";
import { FileInputMultipleFactory } from "./components/file_input_multiple/factory"
import { ErrorPageFactory } from "./components/error_page/factory"
import { QuestionnaireFactory } from "./components/questionnaire/factory"

function App() {
  return (
    <div className="App">
      <ScriptHostComponent
        workerUrl="./d3i_py_worker.js"
        standalone={process.env.NODE_ENV !== "production"}
        factories={[
          new DataSubmissionPageFactory({
            promptFactories: [
                new ConsentFormVizFactory(),
                new FileInputMultipleFactory(),
                new ErrorPageFactory(),
                new QuestionnaireFactory(),
            ],
          }),
        ]}
      />
    </div>
  );
}

export default App;
