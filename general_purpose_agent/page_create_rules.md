# Blazor Server CRUD Pages Rules v2.0

These rules define how to implement CRUD (Create, Read, Update, Delete) pages in Blazor Server applications that leverage the Generic Services architecture defined in `blazor_server_services_rules_generics_v2.0.md`. They standardize layout, component usage, and user experience to ensure maintainability, performance, and consistency.

## IMPORTANT: Implementation Requirements

Before creating any CRUD pages, ensure the following:

1. **Working Directory**: Execute all commands from the `dotnet-blazor-server` directory
2. **Directory Structure**: Create the `Pages` directory if it doesn't exist
3. **Entity Subdirectory**: Create a subdirectory under `Pages` for the specific entity (e.g., `Pages/AdjustmentEntity/`)
4. **File Naming**: Use exact naming convention: `Pages/{EntityName}/{PageType}.razor`
5. **Build Verification**: Use build_and_watch_agent MCP server for build management:
   - Call `check_build_status` to verify current build state
   - If errors exist, call `fix_build_with_lock` to resolve issues automatically
   - Ensure build succeeds before completing page generation
6. **Error Handling**: Use MCP server tools to handle build errors systematically

## 1. Guiding Principles

- **Consistency**: All CRUD pages must look and behave the same across the application.
- **Reusability**: Use shared Tailwind-based components for tables, modals, forms, pagination, and toasts.
- **Performance**: Optimize rendering and data fetching for Blazor Server's real-time SignalR model.
- **UX & Accessibility**: Favor responsive layouts, keyboard accessibility, and clear user feedback.
- **Operation-Focused Services**: Pages must work with the operation-specific generic service interfaces.

## 2. Folder Structure

Each entity should have its own folder under `/Pages`, containing:

```
/Pages/<EntityName>/
   Index.razor     (list & search view)
   Create.razor    (modal or page)
   Edit.razor      (modal or page)
   Details.razor   (read-only view)
```

- Index.razor is the main list view (`@page "/<entityname>"`).
- Create/Edit should prefer modals rather than full navigation, unless a page is explicitly required.

## 3. Shared Components (Required)

All CRUD pages must use the shared components located in `/dotnet-blazor-server/Shared/`:

```
/dotnet-blazor-server/Shared/
   Table.razor
   Modal.razor
   Pagination.razor
   FormInput.razor
   ConfirmDialog.razor
   Toast.razor
   Sidebar.razor
   SkeletonTable.razor
   Enums.cs
   _Imports.razor
   MainLayout.razor
```

Pages should import these components using:
```csharp
@using dotnet-blazor-server.Shared
```

### 3.1 Table Component
- Responsive, scrollable table with Tailwind classes.
- Use `@key` on rows to avoid unnecessary re-renders.
- Allow `<ChildContent>` for rows, and accept a list of headers as a parameter.

### 3.2 Modal Component
- Always render once; toggle visibility using CSS (hidden / flex).
- Must be focus-trapped and closeable via ESC or backdrop click.
- Use Tailwind for spacing, rounded corners, and shadow.

### 3.3 FormInput Component
- Standardized `<input>` styling (border rounded-lg p-2 w-full).
- Automatically renders validation messages under the field.

### 3.4 Pagination Component
- Server-side pagination support (Previous/Next buttons, current page indicator).
- Emits OnPageChanged event to trigger data reloads.

### 3.5 Toast/Alert Component
- Used for global success/error messages after save/delete.
- Styled with Tailwind (green for success, red for errors).

### 3.6 SkeletonTable Component
- Show animated skeleton rows while data loads.

### 3.7 Sidebar Component
- Tailwind accordion for navigation.
- Collapsible per section (domain/module).
- Mobile-friendly toggle button (hamburger menu).

## 4. Generic Service Injection

Pages must properly inject the appropriate operation-specific generic services:

```csharp
// Service interfaces to inject
@inject ICreateCoreEntity<Create{EntityName}Dto> EntityCreator
@inject IGetCoreEntity<{EntityName}Dto> EntityGetter
@inject IUpdateCoreEntity<Update{EntityName}Dto> EntityUpdater
@inject IDeleteCoreEntity<{EntityName}Dto> EntityDeleter
```

## 5. Page Layout & Navigation

Use a main layout with:

- Persistent sidebar (collapsible)
- Header with page title
- Padded main content area

All Index.razor pages must include:

- Search input (with debounced search)
- "New" button (opens create modal)
- Table of results
- Pagination controls
- Empty-state message with CTA when no data exists

## 6. UI/UX Rules

### 6.1 Tables (Index View)
- Keep ≤7 visible columns where possible.
- Allow horizontal scrolling on narrow screens.
- Support sorting on relevant columns.
- Show skeleton loader while loading data.

### 6.2 Modals (Create/Edit/Delete)
- Always use Modal.razor for create/edit.
- Use ConfirmDialog.razor for delete confirmation.
- Keep primary actions (Save/Delete) on the right, secondary actions (Cancel) on the left.
- Use IsLoading/IsSaving parameter to show loading state.

### 6.3 Forms
- Use `<EditForm>` with `<DataAnnotationsValidator />`.
- Show inline validation errors under each field.
- Disable Save button while submitting to prevent double-post.
- Map between DTOs correctly:
  - Use CreateEntityDto for creating new entities
  - Use UpdateEntityDto for updating entities
  - Use EntityDto for reading and deleting entities

#### 6.3.1 Foreign Key Fields - Dropdown Lists
**CRITICAL**: All foreign key properties must be rendered as dropdown lists (select elements) for optimal UX:

- **Implementation**: Use `<InputSelect>` component for all foreign key fields
- **Data Source**: Load related entities using the appropriate `IGetCoreEntity<>` service
- **Display**: Show meaningful text (like Name, Title, Description) rather than just IDs
- **Validation**: Apply proper validation to ensure valid selections
- **Empty State**: Include a "Please select..." or similar option for nullable foreign keys
- **Loading State**: Show loading indicator while related entities are being fetched

**Example Foreign Key Dropdown Implementation**:
```csharp
<!-- For a Customer foreign key in an Order entity -->
<div class="mb-4">
    <label class="block text-sm font-medium text-gray-700 mb-1">Customer</label>
    @if (loadingCustomers)
    {
        <div class="border rounded-lg p-2 w-full bg-gray-100">Loading customers...</div>
    }
    else
    {
        <InputSelect @bind-Value="@(isEditMode ? updateDto.CustomerId : createDto.CustomerId)" 
                     class="border rounded-lg p-2 w-full">
            <option value="">-- Please select a customer --</option>
            @foreach (var customer in availableCustomers)
            {
                <option value="@customer.Id">@customer.Name</option>
            }
        </InputSelect>
    }
    <ValidationMessage For="@(isEditMode ? () => updateDto.CustomerId : () => createDto.CustomerId)" />
</div>
```

**Required Implementation Steps for Foreign Keys**:
1. **Service Injection**: Inject `IGetCoreEntity<>` for each related entity type
2. **Data Loading**: Load related entities in `OnInitializedAsync()`
3. **State Management**: Maintain collections for each foreign key relationship
4. **Error Handling**: Handle loading failures gracefully
5. **Performance**: Consider caching for frequently used lookup data

**Code Pattern for Loading Related Data**:
```csharp
@inject IGetCoreEntity<CustomerDto> CustomerGetter

private List<CustomerDto> availableCustomers = new();
private bool loadingCustomers = true;

protected override async Task OnInitializedAsync()
{
    await Task.WhenAll(
        LoadData(),
        LoadCustomers()
    );
}

private async Task LoadCustomers()
{
    try
    {
        loadingCustomers = true;
        availableCustomers = (await CustomerGetter.GetAllAsync()).ToList();
    }
    catch (Exception ex)
    {
        toast.Show($"Error loading customers: {ex.Message}", ToastType.Error);
    }
    finally
    {
        loadingCustomers = false;
        StateHasChanged();
    }
}
```

### 6.4 Feedback & Errors
- Show success messages in `<Toast>` after create/update/delete.
- Show user-friendly error messages (never raw exception text).
- Display validation failures inline.

## 7. Working with Generic Services

### 7.1 Service Method Signatures

When calling service methods, follow these patterns:

```csharp
// Creating entities
var id = await EntityCreator.CreateAsync<TId>(createDto);

// Getting entities
var entity = await EntityGetter.GetByIdAsync<TId>(id);
var entities = await EntityGetter.GetAllAsync();

// Updating entities
await EntityUpdater.UpdateAsync(updateDto);

// Deleting entities
await EntityDeleter.DeleteAsync(entityDto);
await EntityDeleter.DeleteByIdAsync<TId>(id);
```

### 7.2 Working with DTOs

Each page should handle different DTO types for different operations:

```csharp
// Read operations (list, details)
private List<EntityDto> _entities = new();

// Create operations
private CreateEntityDto _createDto = new();

// Update operations
private UpdateEntityDto _updateDto = new();
```

When editing an entity, map from EntityDto to UpdateEntityDto:

```csharp
private async Task ShowEditModal(int id)
{
    var entity = await EntityGetter.GetByIdAsync<int>(id);
    
    if (entity == null) return;
    
    _updateDto = new UpdateEntityDto
    {
        Id = entity.Id,
        Name = entity.Name,
        // Map other properties
        RowVersion = entity.RowVersion // Important for concurrency!
    };
    
    _isModalOpen = true;
}
```

### 7.3 Exception Handling for Service Operations

Always wrap service calls in try/catch blocks:

```csharp
try
{
    await EntityCreator.CreateAsync<int>(_createDto);
    _toast.Show("Entity created successfully!", ToastType.Success);
    await LoadData();
    CloseModal();
}
catch (Exception ex)
{
    _toast.Show($"Error creating entity: {ex.Message}", ToastType.Error);
}
```

## 8. Performance & Accessibility Rules

- **Async Everywhere**: All service calls must be async.
- **Server-Side Filtering**: Never fetch all rows for large tables.
- **Debounced Search**: Wait ~300ms after typing before reloading data.

### Rendering Optimizations
- Use `@key` on foreach rows.
- Break large pages into child components (e.g., `<EntityTable>`).

### Accessibility
- Semantic HTML (`<table>`, `<form>`, `<button>`).
- Modals must trap focus and restore it after close.
- Sidebar toggle must be keyboard accessible.

## 9. Blazor Server-Specific Optimizations

### 9.1 Circuit Management
- Minimize component state to reduce serialization overhead
- Use `@implements IDisposable` for proper cleanup of subscriptions and events
- Register services as scoped (not singleton) to ensure proper isolation between user circuits

### 9.2 SignalR Connection Handling
- Implement connection resilience with retry logic
- Display clear reconnection UI when circuit is interrupted
- Use `@preservewhitespace false` to reduce DOM size and bandwidth

### 9.3 State Management
- Minimize use of cascading parameters for performance reasons
- Use `StateHasChanged()` sparingly to prevent excessive renders
- Implement efficient state containers for cross-component communication

### 9.4 UI Optimizations
- Virtualize large lists with `<Virtualize>` component
- Defer loading of off-screen content
- Use CSS transitions instead of JS animations where possible

## 10. Example Index.razor

```csharp
@page "/customers"
@inject ICreateCoreEntity<CreateCustomerDto> CustomerCreator
@inject IGetCoreEntity<CustomerDto> CustomerGetter
@inject IUpdateCoreEntity<UpdateCustomerDto> CustomerUpdater
@inject IDeleteCoreEntity<CustomerDto> CustomerDeleter
@implements IDisposable

<PageTitle>Customers</PageTitle>

<div class="p-4">
    <div class="flex justify-between mb-4">
        <input @bind="searchTerm" @bind:event="oninput"
               @oninput="@HandleSearchInput"
               class="border rounded-lg p-2 w-1/3"
               placeholder="Search customers..." />
        <button class="bg-blue-600 text-white px-4 py-2 rounded-lg" @onclick="ShowCreateModal">
            + New Customer
        </button>
    </div>

    @if (isLoading)
    {
        <SkeletonTable RowCount="5" ColumnCount="3" />
    }
    else if (customers.Count == 0)
    {
        <div class="text-center p-4">
            No customers found.
            <button class="underline text-blue-600" @onclick="ShowCreateModal">Create one</button>
        </div>
    }
    else
    {
        <Table Headers="new() { \"Name\", \"Email\", \"Actions\" }">
            @foreach (var c in customers)
            {
                <tr @key="c.Id" class="border-t">
                    <td class="p-3">@c.Name</td>
                    <td class="p-3">@c.Email</td>
                    <td class="p-3 text-right space-x-2">
                        <button class="text-blue-600" @onclick="() => ShowEditModal(c.Id)">Edit</button>
                        <button class="text-red-600" @onclick="() => ConfirmDelete(c)">Delete</button>
                    </td>
                </tr>
            }
        </Table>
        <Pagination TotalCount="totalCount" CurrentPage="currentPage" PageSize="pageSize" OnPageChanged="LoadData" />
    }
</div>

<Modal Title="@(isEditMode ? "Edit Customer" : "Create Customer")" 
       IsOpen="@isModalOpen" 
       OnSave="SaveCustomer" 
       OnCancel="CloseModal"
       IsSaving="isSaving">
    <EditForm Model="@(isEditMode ? updateDto : createDto)" OnValidSubmit="SaveCustomer">
        <DataAnnotationsValidator />

        <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <InputText @bind-Value="@(isEditMode ? updateDto.Name : createDto.Name)" class="border rounded-lg p-2 w-full" />
            <ValidationMessage For="@(isEditMode ? () => updateDto.Name : () => createDto.Name)" />
        </div>

        <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <InputText @bind-Value="@(isEditMode ? updateDto.Email : createDto.Email)" class="border rounded-lg p-2 w-full" />
            <ValidationMessage For="@(isEditMode ? () => updateDto.Email : () => createDto.Email)" />
        </div>
    </EditForm>
</Modal>

<ConfirmDialog Title="Confirm Delete"
               Message="Are you sure you want to delete this customer? This action cannot be undone."
               Type="DialogType.Danger"
               IsOpen="@isConfirmDeleteOpen"
               ConfirmText="Delete"
               OnConfirm="DeleteCustomer"
               OnCancel="CancelDelete" />

<Toast @ref="toast" />

@code {
    private List<CustomerDto> customers = new();
    private CustomerDto selectedCustomer;
    private CreateCustomerDto createDto = new();
    private UpdateCustomerDto updateDto = new();
    private bool isLoading = true;
    private bool isModalOpen = false;
    private bool isEditMode = false;
    private bool isSaving = false;
    private bool isConfirmDeleteOpen = false;
    private string searchTerm = string.Empty;
    private int currentPage = 1;
    private int pageSize = 10;
    private int totalCount;
    private Timer debounceTimer;
    private Toast toast;
    
    protected override async Task OnInitializedAsync() => await LoadData();
    
    protected override void OnAfterRender(bool firstRender)
    {
        if (firstRender)
        {
            debounceTimer = new Timer(300);
            debounceTimer.AutoReset = false;
            debounceTimer.Elapsed += async (sender, args) => 
            {
                await InvokeAsync(async () => 
                {
                    await LoadData();
                    StateHasChanged();
                });
            };
        }
    }
    
    private async Task LoadData()
    {
        try {
            isLoading = true;
            StateHasChanged();
            
            // Get all customers and apply filtering/pagination
            // In a real app, you'd implement server-side filtering and pagination
            var allCustomers = await CustomerGetter.GetAllAsync();
            
            if (!string.IsNullOrWhiteSpace(searchTerm))
            {
                allCustomers = allCustomers.Where(c => 
                    c.Name.Contains(searchTerm, StringComparison.OrdinalIgnoreCase) ||
                    c.Email.Contains(searchTerm, StringComparison.OrdinalIgnoreCase)
                );
            }
            
            totalCount = allCustomers.Count();
            
            // Apply pagination
            customers = allCustomers
                .Skip((currentPage - 1) * pageSize)
                .Take(pageSize)
                .ToList();
        }
        catch (Exception ex) {
            toast.Show($"Error loading data: {ex.Message}", ToastType.Error);
        }
        finally {
            isLoading = false;
            StateHasChanged();
        }
    }
    
    private void HandleSearchInput(ChangeEventArgs e)
    {
        // Debounce search input to prevent excessive server calls
        debounceTimer?.Dispose();
        debounceTimer = new Timer(300);
        debounceTimer.AutoReset = false;
        debounceTimer.Elapsed += async (sender, args) =>
        {
            searchTerm = e.Value?.ToString() ?? string.Empty;
            currentPage = 1; // Reset to first page on new search
            await InvokeAsync(async () =>
            {
                await LoadData();
                StateHasChanged();
            });
        };
        debounceTimer.Start();
    }
    
    private void ShowCreateModal()
    {
        isEditMode = false;
        createDto = new CreateCustomerDto(); // Reset form
        isModalOpen = true;
    }
    
    private async Task ShowEditModal(int id)
    {
        isEditMode = true;
        var customer = await CustomerGetter.GetByIdAsync<int>(id);
        
        if (customer == null)
        {
            toast.Show("Customer not found.", ToastType.Error);
            return;
        }
        
        updateDto = new UpdateCustomerDto
        {
            Id = customer.Id,
            Name = customer.Name,
            Email = customer.Email,
            RowVersion = customer.RowVersion // Important for concurrency
        };
        
        isModalOpen = true;
    }
    
    private void CloseModal() => isModalOpen = false;
    
    private void ConfirmDelete(CustomerDto customer)
    {
        selectedCustomer = customer;
        isConfirmDeleteOpen = true;
    }
    
    private void CancelDelete()
    {
        isConfirmDeleteOpen = false;
        selectedCustomer = null;
    }
    
    private async Task SaveCustomer()
    {
        try {
            isSaving = true;
            
            if (isEditMode)
            {
                await CustomerUpdater.UpdateAsync(updateDto);
                toast.Show("Customer updated successfully!", ToastType.Success);
            }
            else
            {
                await CustomerCreator.CreateAsync<int>(createDto);
                toast.Show("Customer created successfully!", ToastType.Success);
            }
            
            isModalOpen = false;
            await LoadData();
        }
        catch (Exception ex) {
            toast.Show($"Error saving customer: {ex.Message}", ToastType.Error);
        }
        finally {
            isSaving = false;
        }
    }
    
    private async Task DeleteCustomer()
    {
        if (selectedCustomer == null) return;
        
        try {
            await CustomerDeleter.DeleteAsync(selectedCustomer);
            isConfirmDeleteOpen = false;
            selectedCustomer = null;
            toast.Show("Customer deleted successfully!", ToastType.Success);
            await LoadData();
        }
        catch (Exception ex) {
            toast.Show($"Error deleting customer: {ex.Message}", ToastType.Error);
        }
    }
    
    public void Dispose()
    {
        debounceTimer?.Dispose();
    }
}
```

## 11. Quality Checklist (For Every CRUD Page)

- ✅ Proper service interfaces injected (ICreateCoreEntity, IGetCoreEntity, IUpdateCoreEntity, IDeleteCoreEntity)
- ✅ Appropriate DTOs used for each operation (CreateEntityDto, UpdateEntityDto, EntityDto)
- ✅ Shared components used (Table, Modal, FormInput, Pagination, Toast)
- ✅ Async calls everywhere
- ✅ Pagination & filtering implemented 
- ✅ `@key` used on loops
- ✅ Skeleton loaders on first load
- ✅ Inline validation & error handling
- ✅ Mobile-friendly sidebar
- ✅ Modals focus-trapped + ESC close
- ✅ Toast message after CRUD actions
- ✅ Error handling for failed service calls
- ✅ Loading states for all async operations
- ✅ Proper disposal of timers and subscriptions
- ✅ Debounced search implemented
- ✅ Circuit size optimization
- ✅ **Foreign keys implemented as dropdown lists** using `<InputSelect>`
- ✅ **Related entity services injected** for foreign key lookups
- ✅ **Loading states for dropdown data** with proper error handling
- ✅ **Meaningful display values** in dropdowns (not just IDs)

## 12. Advanced Features

### 12.1 Paged Data Retrieval

If your service implements paged data retrieval:

```csharp
private async Task LoadData()
{
    try {
        isLoading = true;
        StateHasChanged();
        
        // Use paged data retrieval if available
        var result = await EntityGetter.GetPagedAsync(
            pageNumber: currentPage,
            pageSize: pageSize,
            searchTerm: searchTerm,
            sortField: sortField,
            ascending: sortAscending);
            
        entities = result.Items.ToList();
        totalCount = result.TotalCount;
    }
    catch (Exception ex) {
        toast.Show($"Error loading data: {ex.Message}", ToastType.Error);
    }
    finally {
        isLoading = false;
        StateHasChanged();
    }
}
```

### 12.2 Handling Concurrency Conflicts

When using RowVersion for optimistic concurrency:

```csharp
try {
    await EntityUpdater.UpdateAsync(updateDto);
    // Success handling
}
catch (DbUpdateConcurrencyException) {
    toast.Show("This record was modified by another user. Please refresh and try again.", ToastType.Warning);
    await LoadData();
}
catch (Exception ex) {
    toast.Show($"Error updating entity: {ex.Message}", ToastType.Error);
}
```

## 13. Sub-Agent Implementation Guidelines

When implementing a CRUD page generator for Blazor Server with Generic Services, the sub-agent should:

### 13.1 Input Processing Requirements
- Accept model class name as input
- Identify required service interfaces from DI container
- Extract property information from model class (names, types, required/optional status)
- Identify primary key property for CRUD operations
- **Detect foreign key properties** and determine related entity types
- **Identify display properties** for foreign key entities (Name, Title, Description, etc.)

### 13.2 Component Generation Process
1. Create the directory structure first (`/Pages/{EntityName}/`)
2. Generate Index.razor with complete implementation
3. Create any required modal components
4. Implement proper binding between components and services

### 13.3 Service Integration
- Properly inject the required generic service interfaces
- Match DTO types for different operations (Create, Read, Update, Delete)
- Handle pagination parameters correctly
- Implement proper error handling for all service calls
- **Inject IGetCoreEntity services for all foreign key related entities**
- **Generate foreign key dropdown loading methods** for each relationship

### 13.4 Implementation Requirements
- Include all required error handling
- Implement debounce for search inputs
- Create proper form validation
- Ensure all state is properly initialized and managed
- Add IDisposable implementation when using timers or subscriptions
- **Generate `<InputSelect>` elements for all foreign key properties**
- **Create loading methods and state management for dropdown data**
- **Implement proper error handling for foreign key data loading**

### 13.5 Example Generation Command
```
generate-crud-pages --model Customer --output Pages/Customers
```

### 13.6 Output Validation
The sub-agent should validate generated code by checking:
- Correct syntax and compilation
- All required components are implemented
- Proper error handling is in place
- Services are correctly injected and used
- Pagination and filtering functionality works
- **Foreign key dropdowns are properly implemented with `<InputSelect>`**
- **Related entity services are correctly injected and used**
- **Loading states and error handling for dropdown data are present**

## Conclusion

These rules provide a comprehensive framework for implementing CRUD pages that work with the Generic Services architecture. By following these guidelines, developers can create consistent, maintainable, and user-friendly interfaces for data management in Blazor Server applications.

## Additional Shared Components Information

The following additional shared components are available and should be used in CRUD pages:

### Enums.cs
Contains shared enumeration definitions used across the application for consistent data types and values.

### _Imports.razor  
Contains common using statements and component imports that are automatically available to all Razor components in the application.

### MainLayout.razor
The main layout component that provides the overall page structure, including:
- Responsive sidebar navigation
- Header section
- Main content area
- Footer
- Uses Tailwind CSS for styling and responsive design
