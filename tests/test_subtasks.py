import os
import pytest
from clickup_apiV2.client import Client


class TestSubtasks:
    @pytest.fixture
    def client(self):
        """Create a ClickUp client with API token from environment variables."""
        api_token = os.getenv('CLICKUP_API_TOKEN')
        if not api_token:
            pytest.skip("CLICKUP_API_TOKEN environment variable not set")
        return Client(api_token)

    @pytest.fixture
    def test_list_id(self):
        """Get list ID from environment variables."""
        list_id = os.getenv('CLICKUP_TEST_LIST_ID')
        if not list_id:
            pytest.skip("CLICKUP_TEST_LIST_ID environment variable not set")
        return list_id

    def test_get_list_tasks_with_subtasks(self, client, test_list_id):
        """Test that get_list_tasks returns subtasks when subtasks=True."""
        # Get tasks with subtasks enabled
        tasks_with_subtasks = client.get_list_tasks(
            test_list_id,
            subtasks=True,
            include_closed=True,
            debug=True
        )

        assert tasks_with_subtasks is not None, "API call should return data"
        assert "tasks" in tasks_with_subtasks, "Response should contain 'tasks' key"

        tasks = tasks_with_subtasks["tasks"]

        # Check if any tasks have subtasks
        has_subtasks = False
        for task in tasks:
            if "subtasks" in task and len(task["subtasks"]) > 0:
                has_subtasks = True
                print(f"Found task {task['id']} with {len(task['subtasks'])} subtasks")
                break

        # If no subtasks found, still pass but log it
        if not has_subtasks:
            print("No subtasks found in the response - this might be expected if no tasks have subtasks")

    def test_get_list_tasks_without_subtasks(self, client, test_list_id):
        """Test that get_list_tasks returns different data when subtasks=False."""
        # Get tasks without subtasks
        tasks_without_subtasks = client.get_list_tasks(
            test_list_id,
            subtasks=False,
            include_closed=True,
            debug=True
        )

        assert tasks_without_subtasks is not None, "API call should return data"
        assert "tasks" in tasks_without_subtasks, "Response should contain 'tasks' key"

    def test_subtasks_parameter_comparison(self, client, test_list_id):
        """Compare responses with and without subtasks parameter."""
        # Get tasks with subtasks
        with_subtasks = client.get_list_tasks(
            test_list_id,
            subtasks=True,
            include_closed=True
        )

        # Get tasks without subtasks
        without_subtasks = client.get_list_tasks(
            test_list_id,
            subtasks=False,
            include_closed=True
        )

        assert with_subtasks is not None, "With subtasks call should succeed"
        assert without_subtasks is not None, "Without subtasks call should succeed"

        # Both should have tasks
        assert "tasks" in with_subtasks
        assert "tasks" in without_subtasks

        # Print comparison for debugging
        print(f"With subtasks: {len(with_subtasks['tasks'])} tasks")
        print(f"Without subtasks: {len(without_subtasks['tasks'])} tasks")

        # Check if any task in with_subtasks has subtask data
        subtask_fields_found = False
        for task in with_subtasks["tasks"]:
            if "subtasks" in task:
                subtask_fields_found = True
                print(f"Task {task['id']} has subtasks field with {len(task['subtasks'])} items")
                break

        if not subtask_fields_found:
            print("No 'subtasks' field found in any task - check API response structure")

    def test_short_format_with_subtasks(self, client, test_list_id):
        """Test short format response with subtasks enabled."""
        tasks = client.get_list_tasks(
            test_list_id,
            format="short",
            subtasks=True,
            include_closed=True
        )

        assert tasks is not None, "Short format call should succeed"
        assert isinstance(tasks, list), "Short format should return a list"

        # Check structure of short format
        if tasks:
            task = tasks[0]
            assert "id" in task, "Short format should include task id"
            assert "name" in task, "Short format should include task name"
            assert "status" in task, "Short format should include task status"

            print(f"Short format returned {len(tasks)} tasks")
            print(f"First task: {task}")

    def test_examine_task_structure(self, client, test_list_id):
        """Examine the full structure of task responses to understand subtasks handling."""
        # Get tasks with subtasks enabled
        response = client.get_list_tasks(
            test_list_id,
            subtasks=True,
            include_closed=True
        )

        assert response is not None, "API call should return data"
        assert "tasks" in response, "Response should contain 'tasks' key"

        tasks = response["tasks"]
        if tasks:
            # Examine the first task in detail
            first_task = tasks[0]
            print(f"\n=== FULL TASK STRUCTURE ===")
            print(f"Task ID: {first_task.get('id')}")
            print(f"Task Name: {first_task.get('name')}")
            print(f"All available fields:")
            for key, value in first_task.items():
                if isinstance(value, (list, dict)):
                    print(f"  {key}: {type(value).__name__} (length: {len(value) if isinstance(value, list) else 'N/A'})")
                else:
                    print(f"  {key}: {value}")

            # Look for any field that might contain subtasks
            potential_subtask_fields = []
            for key, value in first_task.items():
                if isinstance(value, list) and len(value) > 0:
                    potential_subtask_fields.append(key)
                elif 'sub' in key.lower() or 'child' in key.lower():
                    potential_subtask_fields.append(key)

            if potential_subtask_fields:
                print(f"\nPotential subtask fields found: {potential_subtask_fields}")
                for field in potential_subtask_fields:
                    print(f"  {field}: {first_task[field]}")
            else:
                print("\nNo potential subtask fields found")

    def test_examine_full_response_structure(self, client, test_list_id):
        """Examine the complete API response structure to find subtasks."""
        print("\n=== EXAMINING FULL API RESPONSE ===")

        # Get response with subtasks
        response_with_subtasks = client.get_list_tasks(
            test_list_id,
            subtasks=True,
            include_closed=True
        )

        # Get response without subtasks
        response_without_subtasks = client.get_list_tasks(
            test_list_id,
            subtasks=False,
            include_closed=True
        )

        print(f"Response WITH subtasks - top level keys: {list(response_with_subtasks.keys())}")
        print(f"Response WITHOUT subtasks - top level keys: {list(response_without_subtasks.keys())}")

        # Check if there are different keys between responses
        with_keys = set(response_with_subtasks.keys())
        without_keys = set(response_without_subtasks.keys())

        if with_keys != without_keys:
            print(f"Different keys found!")
            print(f"Only in WITH subtasks: {with_keys - without_keys}")
            print(f"Only in WITHOUT subtasks: {without_keys - with_keys}")

        # Compare task counts
        tasks_with = response_with_subtasks.get('tasks', [])
        tasks_without = response_without_subtasks.get('tasks', [])

        print(f"Tasks with subtasks=True: {len(tasks_with)}")
        print(f"Tasks with subtasks=False: {len(tasks_without)}")

        if len(tasks_with) != len(tasks_without):
            print(f"DIFFERENT TASK COUNTS! Difference: {len(tasks_with) - len(tasks_without)}")
            print("This suggests subtasks are returned as separate task objects!")

            # Look for tasks that might be subtasks
            with_ids = {task['id'] for task in tasks_with}
            without_ids = {task['id'] for task in tasks_without}

            subtask_ids = with_ids - without_ids
            if subtask_ids:
                print(f"Potential subtask IDs: {list(subtask_ids)[:10]}...")  # Show first 10

                # Examine a potential subtask
                for task in tasks_with:
                    if task['id'] in subtask_ids:
                        print(f"\n=== POTENTIAL SUBTASK STRUCTURE ===")
                        print(f"Subtask ID: {task['id']}")
                        print(f"Subtask Name: {task.get('name')}")
                        print(f"Parent: {task.get('parent')}")
                        print(f"Top Level Parent: {task.get('top_level_parent')}")
                        break

        # Look for any other differences in the response structure
        for key in response_with_subtasks.keys():
            if key != 'tasks':
                val_with = response_with_subtasks[key]
                val_without = response_without_subtasks.get(key)
                if val_with != val_without:
                    print(f"Difference in {key}: WITH={val_with}, WITHOUT={val_without}")

    def test_check_parent_child_relationships(self, client, test_list_id):
        """Check if any tasks have parent-child relationships indicating subtasks."""
        print("\n=== CHECKING PARENT-CHILD RELATIONSHIPS ===")

        # Get response with subtasks
        response = client.get_list_tasks(
            test_list_id,
            subtasks=True,
            include_closed=True
        )

        tasks = response.get('tasks', [])
        print(f"Total tasks: {len(tasks)}")

        # Look for tasks with parent relationships
        parent_tasks = []
        child_tasks = []

        for task in tasks:
            parent = task.get('parent')
            if parent:
                child_tasks.append({
                    'id': task['id'],
                    'name': task['name'],
                    'parent': parent
                })
            else:
                parent_tasks.append({
                    'id': task['id'],
                    'name': task['name']
                })

        print(f"Tasks with no parent (potential parent tasks): {len(parent_tasks)}")
        print(f"Tasks with parent (potential subtasks): {len(child_tasks)}")

        if child_tasks:
            print(f"\nFound {len(child_tasks)} potential subtasks!")
            for i, subtask in enumerate(child_tasks[:5]):  # Show first 5
                print(f"  Subtask {i+1}: {subtask['name']} (ID: {subtask['id']}) -> Parent: {subtask['parent']}")

        if parent_tasks:
            print(f"\nFirst 5 parent tasks:")
            for i, parent in enumerate(parent_tasks[:5]):
                print(f"  Parent {i+1}: {parent['name']} (ID: {parent['id']})")

        # Count how many child tasks each parent has
        if child_tasks:
            parent_counts = {}
            for child in child_tasks:
                parent_id = child['parent']
                parent_counts[parent_id] = parent_counts.get(parent_id, 0) + 1

            print(f"\nParent task subtask counts:")
            for parent_id, count in parent_counts.items():
                parent_name = next((t['name'] for t in tasks if t['id'] == parent_id), 'Unknown')
                print(f"  {parent_name} ({parent_id}): {count} subtasks")

    def test_count_exact_differences_and_pagination(self, client, test_list_id):
        """Test exact count differences and check if pagination affects subtasks."""
        print("\n=== TESTING EXACT DIFFERENCES AND PAGINATION ===")

        # Test with different page sizes to see if subtasks appear
        page_sizes = [10, 25, 50, 100]

        for page_size in page_sizes:
            print(f"\n--- Testing with page size {page_size} ---")

            # With subtasks
            response_with = client.get_list_tasks(
                test_list_id,
                subtasks=True,
                include_closed=True,
                page_size=page_size
            )

            # Without subtasks
            response_without = client.get_list_tasks(
                test_list_id,
                subtasks=False,
                include_closed=True,
                page_size=page_size
            )

            tasks_with = len(response_with.get('tasks', []))
            tasks_without = len(response_without.get('tasks', []))

            print(f"  With subtasks: {tasks_with} tasks")
            print(f"  Without subtasks: {tasks_without} tasks")
            print(f"  Difference: {tasks_with - tasks_without}")

            if tasks_with != tasks_without:
                print(f"  FOUND DIFFERENCE! Subtasks are being returned!")

                # Get the task IDs that are different
                ids_with = {task['id'] for task in response_with.get('tasks', [])}
                ids_without = {task['id'] for task in response_without.get('tasks', [])}

                subtask_ids = ids_with - ids_without
                parent_only_ids = ids_without - ids_with

                if subtask_ids:
                    print(f"  Subtask IDs found: {list(subtask_ids)[:5]}...")
                if parent_only_ids:
                    print(f"  Parent-only IDs: {list(parent_only_ids)[:5]}...")

                return  # Found the difference, no need to test other page sizes

        # Test without pagination limits
        print(f"\n--- Testing without pagination limits ---")
        response_unlimited_with = client.get_list_tasks(
            test_list_id,
            subtasks=True,
            include_closed=True
        )

        response_unlimited_without = client.get_list_tasks(
            test_list_id,
            subtasks=False,
            include_closed=True
        )

        unlimited_with = len(response_unlimited_with.get('tasks', []))
        unlimited_without = len(response_unlimited_without.get('tasks', []))

        print(f"  Unlimited with subtasks: {unlimited_with} tasks")
        print(f"  Unlimited without subtasks: {unlimited_without} tasks")
        print(f"  Difference: {unlimited_with - unlimited_without}")

        # Check if the 28 subtasks you mentioned might be in a different response field
        print(f"\n--- Checking response metadata ---")
        print(f"  With subtasks response keys: {list(response_unlimited_with.keys())}")

        # Look for any field that might contain count information
        for key, value in response_unlimited_with.items():
            if isinstance(value, (int, dict)) and key != 'tasks':
                print(f"  {key}: {value}")


    def test_direct_url_verification(self, client, test_list_id):
        """Test the direct URL you mentioned that works: subtasks=true&include_closed=true"""
        print("\n=== TESTING DIRECT URL THAT YOU MENTIONED WORKS ===")

        import requests

        # Test using the exact URL pattern you mentioned works
        url = f"https://api.clickup.com/api/v2/list/{test_list_id}/task?subtasks=true&include_closed=true"
        headers = {
            "Content-Type": "application/json",
            "Authorization": client.api_token
        }

        print(f"Testing URL: {url}")

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            print(f"Status: {response.status_code}")
            print(f"Total tasks returned: {len(data.get('tasks', []))}")

            # Count tasks with parents (potential subtasks)
            tasks_with_parents = 0
            tasks_without_parents = 0

            for task in data.get('tasks', []):
                if task.get('parent'):
                    tasks_with_parents += 1
                    print(f"  Subtask found: {task['name']} (Parent: {task['parent']})")
                else:
                    tasks_without_parents += 1

            print(f"Tasks with parents (subtasks): {tasks_with_parents}")
            print(f"Tasks without parents: {tasks_without_parents}")

            if tasks_with_parents > 0:
                print(f"SUCCESS: Found {tasks_with_parents} subtasks using your working URL!")
            else:
                print("No subtasks found - this might mean no tasks in this list have subtasks")

            # Compare with our client method
            client_response = client.get_list_tasks(test_list_id, subtasks=True, include_closed=True)
            client_tasks = len(client_response.get('tasks', []))

            print(f"Direct URL tasks: {len(data.get('tasks', []))}")
            print(f"Client method tasks: {client_tasks}")

            if len(data.get('tasks', [])) == client_tasks:
                print("✓ Client method returns same count as direct URL")
            else:
                print("✗ Different counts - there might be an issue with the client method")

        except requests.exceptions.RequestException as e:
            print(f"Error with direct URL: {e}")
            assert False, f"Direct URL test failed: {e}"


    def test_debug_pagination_parameters(self, client, test_list_id):
        """Debug pagination parameters to understand why we're not getting all tasks."""
        print("\n=== DEBUGGING PAGINATION PARAMETERS ===")

        import requests

        # Test various parameter combinations to match the working direct URL
        test_params = [
            {},  # No additional params
            {"page": 0},
            {"page": 1},
            {"limit": 100},
            {"page_size": 100},
            {"per_page": 100},
            {"archived": False},
            {"order_by": "created"},
            {"reverse": True},
        ]

        base_params = {"subtasks": True, "include_closed": True}

        for i, extra_params in enumerate(test_params):
            params = {**base_params, **extra_params}

            print(f"\nTest {i+1}: {params}")

            # Use client method
            try:
                response = client.get_list_tasks(test_list_id, **params)
                client_count = len(response.get('tasks', []))
                print(f"  Client method: {client_count} tasks")
            except Exception as e:
                print(f"  Client method failed: {e}")
                client_count = 0

            # Use direct API call
            try:
                url = f"https://api.clickup.com/api/v2/list/{test_list_id}/task"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": client.api_token
                }
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                direct_count = len(data.get('tasks', []))
                print(f"  Direct API: {direct_count} tasks")

                if direct_count == 100:
                    print(f"  *** FOUND WORKING PARAMETERS: {params} ***")

                    # Check subtasks
                    subtask_count = sum(1 for task in data.get('tasks', []) if task.get('parent'))
                    print(f"  Subtasks found: {subtask_count}")

            except Exception as e:
                print(f"  Direct API failed: {e}")
                direct_count = 0

            if client_count != direct_count:
                print(f"  ⚠️  MISMATCH: Client={client_count}, Direct={direct_count}")


    def test_exact_mimic_working_url(self, client, test_list_id):
        """Test that exactly mimics the working direct URL approach."""
        print("\n=== EXACT MIMIC OF WORKING URL ===")

        import requests

        # First: Test the exact working URL approach
        working_url = f"https://api.clickup.com/api/v2/list/{test_list_id}/task?subtasks=true&include_closed=true"
        headers = {
            "Content-Type": "application/json",
            "Authorization": client.api_token
        }

        print(f"Working URL: {working_url}")
        response = requests.get(working_url, headers=headers)
        working_data = response.json()
        working_count = len(working_data.get('tasks', []))
        working_subtasks = sum(1 for task in working_data.get('tasks', []) if task.get('parent'))

        print(f"Working approach: {working_count} tasks, {working_subtasks} subtasks")

        # Second: Test client method with same exact parameters
        client_data = client.get_list_tasks(test_list_id, subtasks=True, include_closed=True)
        client_count = len(client_data.get('tasks', []))
        client_subtasks = sum(1 for task in client_data.get('tasks', []) if task.get('parent'))

        print(f"Client method: {client_count} tasks, {client_subtasks} subtasks")

        # Third: Check if they match
        if working_count == client_count and working_subtasks == client_subtasks:
            print("✅ SUCCESS: Client method now matches working URL!")
        else:
            print("❌ MISMATCH: Client method still differs from working URL")

            # Debug: Check if task IDs are the same
            working_ids = {task['id'] for task in working_data.get('tasks', [])}
            client_ids = {task['id'] for task in client_data.get('tasks', [])}

            missing_in_client = working_ids - client_ids
            extra_in_client = client_ids - working_ids

            if missing_in_client:
                print(f"Missing in client: {len(missing_in_client)} tasks")
                print(f"First 5 missing IDs: {list(missing_in_client)[:5]}")

            if extra_in_client:
                print(f"Extra in client: {len(extra_in_client)} tasks")
                print(f"First 5 extra IDs: {list(extra_in_client)[:5]}")


if __name__ == "__main__":
    # Example of how to run the test manually
    print("To run this test, set the following environment variables:")
    print("export CLICKUP_API_TOKEN='your_api_token'")
    print("export CLICKUP_TEST_LIST_ID='your_list_id'")
    print("\nThen run: pytest tests/test_subtasks.py -v -s")
