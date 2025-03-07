# Current task implementation manifest

Внимательно прочитай спецификацию задачи;
составь план выполнения задачи и помести его в этот файл;
пункты плана должны поддерживать возможность отметки об исполнении;
первым пунктом плана всегда должен быть прогон всех юнит-тестов с фиксацией результата 
(не все тесты обязательно должны проходить);
при выполнении задачи нужно строго придерживаться методологии TDD;
прежде чем модифицировать существующий и/или добавлять новый код, 
нужно написать все необходимые тесты на этот модифицируемый или новый код;
при модификации существующего кода, следует сначала модифицировать имеющиеся тесты, 
относящиеся к этому коду, с учетом его планируемых изменений;
последним пунктом плана всегда должен быть прогон всех юнит-тестов;
этот пункт считается завершённым только когда все тесты проходят;
план должен состоять из трёх частей:
первая часть - написание/модификация всех необходимых юнит-тестов
вторая часть - написание кода, который полностью совсместим с уже имеющимися юнит-тестами;
третья часть - контрольный прогон всех юнит-тестов с новым кодом;
после того, как план создан приступай к его последовательному исполнению, отмечая выполненные пункты в этом файле;

## Task specification

должно быть 4 независимых области скриншота и четыре независимых сценария кликов;
в каждом сценарии кликов должно быть возможно произвольное количество кликов, начиная с нуля;
все клики должны быть разделены 2-секундными паузами;
когда я в гуи меняю координаты скриншота, они должны меняться только для той области, которая выбрана в гуи в качестве текущей,
а не для всех сразу, как сейчас;
для каждой области экрана (для каждого скриншота) должен быть свой независимый запрос к распознающей изображение модели;

No independent click scenarios: There's only one global should_click flag that's set to True if any area has a detection. This means all areas share the same click decision.
No 2-second pauses between clicks: The clicks happen immediately when the detection results are processed, with no pause between them.
Click triggers in two places: Clicks are triggered both directly in the agent_loop for areas 2 and 3 (for "primary test" detection) AND via the workflow for all areas.
No support for arbitrary number of clicks: The current implementation doesn't have a way to trigger multiple clicks in a sequence for each area.
To implement the requirements, we would need to:
Modify AgentState to track independent should_click flags for each area
Update ScreenSpyAgent to check each area individually and perform clicks with 2-second pauses
Move all click logic to one place (either directly in agent_loop or in the workflow)
Add support for sequences of clicks with the possibility of zero clicks

## Implementation Plan

### Part 1: Writing/Modifying Unit Tests


### Part 2: Implementing Code Changes


### Part 3: Final Testing





